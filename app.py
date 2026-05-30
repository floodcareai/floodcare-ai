import os
from flask import Flask, request

from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage
from linebot.exceptions import InvalidSignatureError

app = Flask(__name__)

line_bot_api = LineBotApi(
    os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
)

handler = WebhookHandler(
    os.getenv("LINE_CHANNEL_SECRET")
)

@app.route("/")
def home():
    return "FLOODCARE AI is running"

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]

    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return "Invalid signature", 400

    return "OK"

from linebot.models.events import MessageEvent
from linebot.models import TextMessage

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text=f"คุณพิมพ์ว่า: {user_text}"
        )
    )

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
