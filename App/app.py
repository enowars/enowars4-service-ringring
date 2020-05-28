from flask import Flask, render_template, request, make_response
import re
import datetime
import logging
from utils import debug, db_helper
from utils.invoices_connector import add_to_invoice, get_invoices, request_bill
import json
import uuid
from flask_table import Table, Col
import ast

app = Flask(__name__)

logger = logging.getLogger('RingRing')
logger.setLevel(logging.INFO)

AVAILABLE_FOOD = ['pizza', 'bred', 'fish']


# handler = logging.FileHandler(os.environ['LOGDIR'])
# formatter = logging.Formatter("%(name)s - %(levelname)s - %(levelno)s - %(message)s")
# handler.setFormatter(formatter)
# logger.addHandler(handler)

@app.route('/')
def home():
    response = make_response(render_template('home.html'))

    if not request.cookies.get('session_id'):
        session_id = str(uuid.uuid4())
        response.set_cookie('session_id', session_id)
        db_helper.add_session(session_id)

    return response


@app.route('/get_bot_response')
def get_bot_response():
    user_text = request.args.get('msg')
    state = request.args.get('state')
    if state:
        state = json.loads(state)
    else:
        state = {'mode': 'main_menu'}

    if (state and state['mode'] == 'alarm') or (re.search('alarm', user_text)):
        return set_alarm(user_text, state)

    elif re.search('lonely', user_text) or re.search('bored', user_text):
        return {'response': 'Go to /guests to see how other guests are doing.'}

    elif re.search('food', user_text) or (state and state['mode'] == 'food_order'):
        return order_food(user_text, state)

    elif (state and state['mode'] == 'invoice') or (re.search('invoice', user_text)):
        return make_invoice(user_text, state)
    else:
        # logger.debug('Something very secret.')
        return {'response': '''I have no service registered to that request. These are the services that I can provoide: <br>
        - set an alarm <br>
        - order champaign <br>
        - ...
        ''',
                'state': json.dumps({'mode': 'main_menu'})}


@app.route('/alarm', methods=['GET'])
def alarm():
    class ItemTable(Table):
        time = Col('time')
        text = Col('text')

    # TODO: add alarm overview page (potentially just a dead end)
    items = db_helper.get_alarms(request.cookies.get('session_id'))
    table = ItemTable(items)

    return render_template('service.html', service_description='These are your alarms.', table=table)


@app.route('/invoices', methods=['GET'])
def invoices():
    guest_name = request.cookies.get('session_id')
    guest_invoices = get_invoices(guest_name)

    class InvoiceItemTable(Table):
        invoice_number = Col('Invoice Number')
        item = Col('Item')
        name = Col('Guest Name')
        amount = Col('Amount')

    return make_response(render_template('service.html', service_description='These are your invoices.',
                                         table=InvoiceItemTable(guest_invoices)))


@app.route('/guests', methods=['GET'])
def guests():
    class ItemTable(Table):
        guest_id = Col('guest_id')

    items = db_helper.get_paying_sessions()
    table = ItemTable(items)

    return render_template('service.html',
                           service_description='If you are bored, then go and visists some of our other guests.',
                           table=table)


@app.route('/make_me_a_vip', methods=['POST'])
def make_me_a_vip():
    session_id = request.cookies.get('session_id')
    db_helper.make_vip(session_id)

    recalc = request.form.get('recalc')
    if recalc:
        try:
            vips_are_billable = ast.literal_eval(recalc)
        except ValueError:
            return {'response': 'recalc must be either True or False'}
        db_helper.update_invoicing(vips_are_billable)

    return {'response': 'Success.'}


@debug(logger=logger, _debug=False)
def set_alarm(user_text, state):
    session_id = request.cookies.get('session_id')
    mode = state['mode']
    if mode == 'alarm':
        if 'alarm_time' in state:
            alarm_time = state['alarm_time']
            try:
                logger.debug(f'{session_id}: Set alarm text to: {user_text}.')
                db_helper.insert_alarm(session_id, alarm_time, user_text)
                return {
                    'response': f'Alarm text set to {user_text}. <br>Do you want to pay [now] or put it on your [room-bill]?',
                    'state': json.dumps({'mode': 'alarm', 'payment': 'pending'})}
            except ValueError:
                return {'response': 'This was not a valid input. Try again.',
                        'state': json.dumps({'mode': 'alarm',
                                             'alarm_time': alarm_time})}
        elif 'payment' in state:
            if user_text not in ('now', 'room-bill'):
                return {'response': 'This was not a valid input. Try [now] or [room-bill].',
                        'state': json.dumps({'mode': 'alarm', 'payment': 'pending'})}
            else:
                add_to_invoice(session_id, 'alarm', payment_method=user_text)
                return {'response': 'Perfect. Thank you very much.',
                        'state': json.dumps({'mode': 'main_menu'})}
        else:
            try:
                alarm_time = datetime.datetime.strptime(user_text, '%H:%M')
                logger.debug(f'{session_id}: Set alarm with time: {alarm_time}.')
                return {
                    'response': f'alarm time set to {user_text}. What do you want us to say, when we wake you up?',
                    'state': json.dumps({'mode': 'alarm',
                                         'alarm_time': user_text})}
            except ValueError:
                return {'response': 'This was not a valid input. Try again.',
                        'state': json.dumps({'mode': 'alarm'})}

    else:
        return {'response': 'For what time do you want to set the alarm? Please use HH:MM.',
                'state': json.dumps({'mode': 'alarm'})}


def make_invoice(user_text, state):
    session_id = request.cookies.get('session_id')
    mode = state['mode']

    if mode == 'invoice':
        if state['invoice_step'] == '1':
            if user_text not in ('y', 'n'):
                return {'response': 'I did not quite get that. Please answer with y or n.',
                        'state': json.dumps({'mode': 'invoice', 'invoice_step': '1'})}
            elif user_text == 'n':
                return {
                    'response': 'No problem. You can pay any time you want. But we will not forget your open bills!',
                    'state': json.dumps({'mode': 'main_menu'})}
            else:
                items, total = request_bill(session_id)
                response_string = "You have paid for the following items: <br>"
                for item in items:
                    response_string = response_string + str(item) + '<br>'
                response_string = response_string + f"""for a total ammount of <b>{total}</b>. <br>
                                    It was a pleasure to have you as our guest. Make sure to come back soon!"""
                return {'response': response_string,
                        'state': json.dumps({'mode': 'main_menu'})}

    else:
        return {'response': 'Do you want to pay your open invoices now?[y or n]',
                'state': json.dumps({'mode': 'invoice', 'invoice_step': '1'})}


def order_food(user_text, state):
    session_id = request.cookies.get('session_id')
    mode = state['mode']
    if mode == 'food_order':
        if state['order_step'] == '1':
            if user_text not in AVAILABLE_FOOD:
                return {
                    'response': 'I did not quite get that. Please choose one of <br> {"<br>".join(AVAILABLE_FOOD)}.',
                    'state': json.dumps({'mode': 'food_order', 'order_step': '1'})}
            else:
                return {'response': 'Anything you want to add to your order? Anything we need to know?',
                        'state': json.dumps({'mode': 'food_order', 'order_step': '2', 'order': user_text})}
        if state['order_step'] == '2':
            order = state['order']
            if user_text == 'No' or user_text == 'no':
                note = None
            else:
                note = user_text
            add_to_invoice(session_id, order, notes=note)
            return {'response': 'Thanks a lot for your order. The Microwave is spinning!',
                    'state': json.dumps({'mode': 'main_menu'})}

    else:
        return {'response': f"""What food do you want to order? You can choose between <br> 
                    {'<br>'.join(AVAILABLE_FOOD)}.<br>
                    I must admit they are all very good. It is going to be a hard choice.""",
                'state': json.dumps({'mode': 'food_order', 'order_step': '1'})}


if __name__ == '__main__':
    app.run(port=7353, host='0.0.0.0')
