from flask import Flask, render_template, request, make_response
import re
import datetime
import logging
from utils import debug, add_to_invoice
import json
import uuid
from flask_table import Table, Col
import db_helper
import ast

app = Flask(__name__)

logger = logging.getLogger('RingRing')
logger.setLevel(logging.INFO)


# handler = logging.FileHandler(os.environ['LOGDIR'])
# formatter = logging.Formatter("%(name)s - %(levelname)s - %(levelno)s - %(message)s")
# handler.setFormatter(formatter)
# logger.addHandler(handler)

# TODO: make endpoint have proper http verbs

@app.route("/")
def home():
    response = make_response(render_template("home.html"))

    if not request.cookies.get('session_id'):
        # TODO is uuid safe or rather use hash?
        session_id = str(uuid.uuid4())
        response.set_cookie('session_id', session_id)
        db_helper.add_session(session_id)

    return response


@app.route("/get_bot_response")
def get_bot_response():
    user_text = request.args.get('msg')
    state = request.args.get('state')
    if state:
        state = json.loads(state)
    else:
        state = {'mode': 'main_menu'}

    if (state and state['mode'] == 'alarm') or (re.search('alarm', user_text)):
        return set_alarm(user_text, state)

    elif re.search('lonely', user_text):
        return {'response': "Go to /guests to see how other guests are doing."}

    else:
        logger.debug("Something very secret.")
        return {'response': """I have no service registered to that request. These are the services that I can provoide: \n
        - set an alarm \n
        - order champaign \n
        - ...
        """,
                'state': json.dumps({'mode': 'main_menu'})}


@app.route("/alarm")
def alarm():
    class ItemTable(Table):
        time = Col('time')
        text = Col('text')

    # TODO: add alarm overview page (potentially just a dead end)
    items = db_helper.get_alarms(request.cookies.get('session_id'))
    table = ItemTable(items)

    return render_template("alarm.html", alarms_table=table)


@app.route("/guests")
def guests():
    class ItemTable(Table):
        guest_id = Col('guest_id')

    items = db_helper.get_paying_sessions()
    table = ItemTable(items)

    return render_template("guests.html", table=table)


@app.route("/make_me_a_vip")
def make_me_a_vip():
    session_id = request.cookies.get('session_id')
    db_helper.make_vip(session_id)

    if 'recalc' in request.args:
        try:
            vips_are_billable = ast.literal_eval(request.args.get('recalc'))
        except ValueError:
            return {'response': 'recalc must be either True or False'}
        db_helper.update_invoicing(vips_are_billable)

    return {'response': 'Sucess.'}


@debug(logger=logger, _debug=False)
def set_alarm(user_text, state):
    session_id = request.cookies.get('session_id')
    mode = state['mode']
    if mode == 'alarm' and 'alarm_time' not in state:
        try:
            alarm_time = datetime.datetime.strptime(user_text, '%H:%M')
            logger.debug(f'{session_id}: Set alarm with time: {alarm_time}.')
            return {
                'response': f"alarm time set to {user_text}. What do you want us to say, when we wake you up?",
                'state': json.dumps({'mode': 'alarm',
                                     'alarm_time': user_text})}
        except ValueError:
            return {'response': "This was not a valid input. Try again.",
                    'state': json.dumps({'mode': 'alarm'})}
    elif 'alarm_time' in state:
        alarm_time = state['alarm_time']
        try:
            logger.debug(f'{session_id}: Set alarm text to: {user_text}.')
            add_to_invoice('alarm', '1.50€')
            db_helper.insert_alarm(session_id, alarm_time, user_text)
            return {'response': f"Alarm text set to {user_text}.", 'state': {'mode': 'main_menu'}}
        except ValueError:
            return {'response': "This was not a valid input. Try again.",
                    'state': json.dumps({'mode': 'alarm',
                                         'alarm_time': alarm_time})}
    else:
        return {'response': "For what time do you want to set the alarm? Please use HH:MM.",
                'state': json.dumps({'mode': 'alarm'})}


if __name__ == "__main__":
    app.run(port=7353, host='0.0.0.0')
