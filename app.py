import os
from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home():
    return "FLOODCARE AI is running"

@app.route("/callback", methods=["POST"])
def callback():
    return "OK"

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
