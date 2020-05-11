from flask import Flask, render_template, request
import re
import datetime
from utils import debug
import logging

app = Flask(__name__)
logger = logging.getLogger('RingRing')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
logger.addHandler(handler)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/get_bot_response")
@debug(logger=logger, _debug=False)
def get_bot_response():
    user_text = request.args.get('msg')
    state = request.args.get('state')
    if (state and state == 'alarm') or (re.search('alarm', user_text)):
        return set_alarm(user_text, state)

    else:
        logger.debug("Something very secret.")
        return {'response': """I have no service registered to that request. These are the services that I can provoide: \n
        - set an alarm \n
        - order champaign \n
        - ...
        """,
                'state': ''}


@app.route("/alarm")
def alarm():
    # TODO: add alarm overview page (potentially just a dead end) bla


def set_alarm(user_text, state):
    if state == 'alarm':
        try:
            alarm_time = datetime.datetime.strptime(user_text, '%H:%M')
            logger.info(f'Set alarm with time: {alarm_time}')
            return {'response': f"alarm time set to {alarm_time.strftime('%H:%M')}.",
                    'state': ''}
        except ValueError:
            return {'response': "This was not a valid input. Try again.",
                    'state': 'alarm'}
    else:
        return {'response': "For what time do you want to set the alarm? Please use HH:MM.",
                'state': 'alarm'}


if __name__ == "__main__":
    app.run()
