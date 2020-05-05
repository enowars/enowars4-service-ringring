from flask import Flask, render_template, request
import re
import datetime

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/get_bot_response")
def get_bot_response():
    userText = request.args.get('msg')
    state = request.args.get('state')
    if state and state == 'alarm':
        try:
            alarm_time = datetime.datetime.strptime(userText, '%H:%M')
            return {'response': f"alarm time set to {alarm_time.strftime('%H:%M')}.", 'state': ''}
        except:
            return {'response': "This was not a valid input. Try again.", 'state': 'alarm'}

    elif re.search('alarm', userText):
        return {'response': "For what time do you want to set the alarm? Please use HH:MM.", 'state': 'alarm'}
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


def set_alarm():
    pass


if __name__ == "__main__":
    app.run()
