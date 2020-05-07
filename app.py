from flask import Flask, render_template, request
import re
import datetime
from utils import dev_mode

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/get_bot_response")
@dev_mode
def get_bot_response():
    user_text = request.args.get('msg')
    state = request.args.get('state')
    if (state and state == 'alarm') or (re.search('alarm', user_text)):
        return set_alarm(user_text, state)

    else:
        return {'response': """I have no service registered to that request. These are the services that I can provoide: \n
        - set an alarm \n
        - order champaign \n
        - ...
        """,
                'state': ''}


@app.route("/alarm")
def alarm():
    pass


def set_alarm(user_text, state):
    if state == 'alarm':
        try:
            alarm_time = datetime.datetime.strptime(user_text, '%H:%M')
            return {'response': f"alarm time set to {alarm_time.strftime('%H:%M')}.",
                    'state': ''}
        except:
            return {'response': "This was not a valid input. Try again.",
                    'state': 'alarm'}
    else:
        return {'response': "For what time do you want to set the alarm? Please use HH:MM.",
                'state': 'alarm'}



if __name__ == "__main__":
    app.run()
