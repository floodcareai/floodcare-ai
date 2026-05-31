import os
import traceback
from flask import Flask, request

import google.generativeai as genai

from linebot.v3.webhook import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent, LocationMessageContent
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
MODEL = os.getenv("MODEL", "gemini-1.5-flash")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

user_locations = {}


@app.route("/")
def home():
    return "FLOODCARE AI is running"


@app.route("/health")
def health():
    missing = []

    if not GEMINI_API_KEY:
        missing.append("GEMINI_API_KEY")
    if not LINE_CHANNEL_ACCESS_TOKEN:
        missing.append("LINE_CHANNEL_ACCESS_TOKEN")
    if not LINE_CHANNEL_SECRET:
        missing.append("LINE_CHANNEL_SECRET")

    if missing:
        return {
            "status": "error",
            "missing": missing,
            "model": MODEL
        }, 500

    return {
        "status": "ok",
        "model": MODEL
    }


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid LINE signature")
        return "Invalid signature", 400
    except Exception as e:
        print("CALLBACK ERROR:", str(e))
        traceback.print_exc()
        return "Callback error", 500

    return "OK"


def cut_text(text, limit=4500):
    text = text or "ขออภัย ระบบไม่สามารถสร้างคำตอบได้"
    return text[:limit]


def send_reply(reply_token, text):
    try:
        text = cut_text(text)

        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[TextMessage(text=text)]
                )
            )

    except Exception as e:
        print("SEND REPLY ERROR:", str(e))
        traceback.print_exc()


def menu():
    return """🌊 FLOODCARE AI

พิมพ์หมายเลขที่ต้องการ

1️⃣ เตรียมตัวก่อนน้ำท่วม
2️⃣ วิธีอพยพ
3️⃣ ชุดยังชีพ
4️⃣ เบอร์ฉุกเฉิน
5️⃣ ปฐมพยาบาล
6️⃣ ศูนย์พักพิง
7️⃣ ตรวจสอบระดับน้ำ
8️⃣ SOS ขอความช่วยเหลือ
9️⃣ ถาม AI เรื่องน้ำท่วม

พิมพ์: เมนู"""


def ask_ai(user_text):
    if not GEMINI_API_KEY:
        return "ERROR: ยังไม่ได้ตั้งค่า GEMINI_API_KEY ใน Render"

    try:
        model = genai.GenerativeModel(MODEL)

        prompt = f"""
คุณคือ FLOODCARE AI
ผู้ช่วยอัจฉริยะด้านน้ำท่วม อุทกภัย การอพยพ และการช่วยเหลือฉุกเฉิน

กติกาการตอบ:
- ตอบเป็นภาษาไทย
- ใช้ภาษาง่าย
- ตอบเป็นข้อ ๆ
- เน้นความปลอดภัย
- ถ้าเป็นเหตุฉุกเฉิน ให้แนะนำโทร 191, 1669 หรือ 1784
- ถ้าไม่แน่ใจ ให้แนะนำติดต่อหน่วยงานในพื้นที่

คำถามผู้ใช้:
{user_text}
"""

        response = model.generate_content(prompt)

        if not response:
            return "ERROR: Gemini ไม่ส่ง response กลับมา"

        if not hasattr(response, "text") or not response.text:
            return "ERROR: Gemini ตอบกลับมาแต่ว่างเปล่า"

        return cut_text(response.text)

    except Exception as e:
        print("GEMINI ERROR:", str(e))
        traceback.print_exc()
        return f"ERROR GEMINI: {str(e)}"


@handler.add(MessageEvent, message=LocationMessageContent)
def handle_location(event):
    try:
        user_id = event.source.user_id

        user_locations[user_id] = {
            "lat": event.message.latitude,
            "lng": event.message.longitude
        }

        reply_text = """📍 ได้รับพิกัดแล้ว

หากต้องการขอความช่วยเหลือ ให้พิมพ์ SOS หรือ 8"""

        send_reply(event.reply_token, reply_text)

    except Exception as e:
        print("LOCATION ERROR:", str(e))
        traceback.print_exc()
        send_reply(event.reply_token, f"ERROR LOCATION: {str(e)}")


@handler.add(MessageEvent, message=TextMessageContent)
def handle_text(event):
    user_text = event.message.text.strip()
    user_id = event.source.user_id

    try:
        if user_text in ["เมนู", "menu", "Menu", "MENU"]:
            reply_text = menu()

        elif user_text == "1":
            reply_text = """🌊 เตรียมตัวก่อนน้ำท่วม

1. ติดตามข่าวจาก ปภ. และหน่วยงานท้องถิ่น
2. ยกของมีค่าและเครื่องใช้ไฟฟ้าขึ้นที่สูง
3. เตรียมน้ำดื่ม อาหารแห้ง และยาประจำตัว
4. เตรียมไฟฉาย power bank และเอกสารสำคัญ
5. วางแผนเส้นทางอพยพ"""

        elif user_text == "2":
            reply_text = """🚶 วิธีอพยพเมื่อน้ำท่วม

1. ปฏิบัติตามคำสั่งเจ้าหน้าที่
2. ปิดไฟ ปิดแก๊ส และล็อกบ้าน
3. หลีกเลี่ยงน้ำเชี่ยวและสายไฟ
4. ไปยังพื้นที่สูงหรือศูนย์พักพิง
5. แจ้งญาติเมื่อถึงที่ปลอดภัย"""

        elif user_text == "3":
            reply_text = """🎒 ชุดยังชีพฉุกเฉิน

- น้ำดื่ม
- อาหารแห้ง
- ยาประจำตัว
- ไฟฉาย
- power bank
- เอกสารสำคัญ
- เงินสด
- เสื้อผ้า
- นกหวีด"""

        elif user_text == "4":
            reply_text = """🚨 เบอร์ฉุกเฉิน

191 ตำรวจ
1669 การแพทย์ฉุกเฉิน
1784 ปภ.
199 ดับเพลิง
1146 กรมทางหลวง
1193 ตำรวจทางหลวง"""

        elif user_text == "5":
            reply_text = """🩹 ปฐมพยาบาลเบื้องต้น

1. ล้างแผลด้วยน้ำสะอาด
2. ปิดแผลเพื่อป้องกันเชื้อโรค
3. หากถูกไฟดูด ห้ามจับตัวผู้ป่วยก่อนตัดไฟ
4. หากจมน้ำ โทร 1669 ทันที
5. หากมีไข้หรือแผลบวมแดง ควรพบแพทย์"""

        elif user_text == "6":
            reply_text = """🏠 ศูนย์พักพิง

ให้ติดต่อ:
1. อบต. หรือเทศบาล
2. ผู้ใหญ่บ้าน / กำนัน
3. ปภ. โทร 1784
4. วัด โรงเรียน หรือศาลาประชาคมใกล้บ้าน"""

        elif user_text == "7":
            reply_text = """📊 ตรวจสอบระดับน้ำ

ระบบต้นแบบยังไม่ได้เชื่อมข้อมูลระดับน้ำจริง

แนะนำให้ตรวจสอบจาก:
1. ปภ. โทร 1784
2. กรมอุตุนิยมวิทยา
3. เทศบาล / อบต.
4. ประกาศจากเจ้าหน้าที่ในพื้นที่"""

        elif user_text == "8" or user_text.upper().startswith("SOS"):
            loc = user_locations.get(user_id)

            if loc:
                location_text = f"พิกัดล่าสุด: {loc['lat']}, {loc['lng']}"
            else:
                location_text = "ยังไม่ได้รับพิกัด กรุณาส่ง Location ใน LINE เพิ่มเติม"

            reply_text = f"""🚨 SOS ขอความช่วยเหลือ

{location_text}

โปรดส่งข้อมูล:
ชื่อ:
เบอร์โทร:
จำนวนผู้ประสบภัย:
ระดับน้ำ:
ต้องการความช่วยเหลือ:

หากฉุกเฉินมาก โทร 191, 1669 หรือ 1784 ทันที"""

        elif user_text == "9":
            reply_text = """🤖 ถาม AI เรื่องน้ำท่วม

พิมพ์คำถามได้เลย เช่น
- น้ำท่วมควรเตรียมตัวอย่างไร
- ไฟดูดช่วงน้ำท่วมป้องกันอย่างไร
- หลังน้ำลดต้องทำอะไร"""

        else:
            reply_text = ask_ai(user_text)

    except Exception as e:
        print("SYSTEM ERROR:", str(e))
        traceback.print_exc()
        reply_text = f"ERROR SYSTEM: {str(e)}"

    send_reply(event.reply_token, reply_text)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
