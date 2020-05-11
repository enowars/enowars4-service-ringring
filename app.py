from flask import Flask, render_template, request, make_response
import re
import datetime
import logging
from utils import debug
import json
import uuid


app = Flask(__name__)

logger = logging.getLogger('RingRing')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
logger.addHandler(handler)

@app.route("/")
def home():
    session_id = str(uuid.uuid4())
    response = make_response(render_template("home.html"))
    response.set_cookie('session_id', session_id)
    return response


@app.route("/get_bot_response")
def get_bot_response():
    session_id = request.cookies.get('session_id')
    user_text = request.args.get('msg')
    state = request.args.get('state')
    if state:
        state = json.loads(state)
    else:
        state = {'mode': 'main_menu'}

    if (state and state['mode'] == 'alarm') or (re.search('alarm', user_text)):
        return set_alarm(user_text, state)

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
    # TODO: add alarm overview page (potentially just a dead end)
    pass


@debug(logger=logger, _debug=False)
def set_alarm(user_text, state):
    mode = state['mode']
    if mode == 'alarm' and 'alarm_time' not in state:
        try:
            alarm_time = datetime.datetime.strptime(user_text, '%H:%M')
            logger.info(f'Set alarm with time: {alarm_time}')
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
            logger.debug(f'Set alarm text to: {user_text}')
            return {'response': f"Alarm text set to {user_text}.", 'state': {'mode': 'main_menu'}}
        except ValueError:
            return {'response': "This was not a valid input. Try again.",
                    'state': json.dumps({'mode': 'alarm', 'alarm_time': alarm_time})}
    else:
        return {'response': "For what time do you want to set the alarm? Please use HH:MM.",
                'state': json.dumps({'mode': 'alarm'})}


if __name__ == "__main__":
    app.run()
