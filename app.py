from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return f"You said {userText}"


if __name__ == "__main__":
    app.run()
