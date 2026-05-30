import os
from flask import Flask, request

from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage
from linebot.exceptions import InvalidSignatureError

import google.generativeai as genai

# ตั้งค่า Gemini API Key จาก Environment Variable
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model_name = os.getenv("MODEL", "gemini-2.5-flash")

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

    # เรียก Gemini API แทน OpenAI
    response = genai.chat(
        model=model_name,
        messages=[
            {"role": "user", "content": user_text}
        ]
    )

    reply_text = response.last.message.content[0].text

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text=reply_text
        )
    )

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
