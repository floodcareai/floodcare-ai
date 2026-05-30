import os
from flask import Flask, request

from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage, TextMessage, LocationMessage
from linebot.models.events import MessageEvent
from linebot.exceptions import InvalidSignatureError

import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = os.getenv("MODEL", "gemini-2.5-flash")

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

user_locations = {}

@app.route("/")
def home():
    return "FLOODCARE AI 3.0 is running"

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return "Invalid signature", 400

    return "OK"

def menu():
    return """🌊 FLOODCARE AI 3.0

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
    model = genai.GenerativeModel(MODEL)

    prompt = f"""
คุณคือ FLOODCARE AI 3.0
ผู้ช่วยอัจฉริยะด้านน้ำท่วม อุทกภัย การอพยพ และการช่วยเหลือฉุกเฉิน

ตอบเป็นภาษาไทย
ใช้ภาษาง่าย
ตอบเป็นข้อ ๆ
เน้นความปลอดภัย
ถ้าเป็นเหตุฉุกเฉิน ให้แนะนำโทร 191, 1669 หรือ 1784

คำถาม:
{user_text}
"""

    response = model.generate_content(prompt)
    return (response.text or "ขออภัย ระบบไม่สามารถสร้างคำตอบได้")[:4500]

@handler.add(MessageEvent)
def handle_message(event):
    try:
        if isinstance(event.message, LocationMessage):
            user_locations[event.source.user_id] = {
                "lat": event.message.latitude,
                "lng": event.message.longitude
            }

            reply_text = """📍 ได้รับพิกัดแล้ว

หากต้องการขอความช่วยเหลือ ให้พิมพ์ SOS หรือ 8"""

        elif isinstance(event.message, TextMessage):
            user_text = event.message.text.strip()

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
4. วัด โรงเรียน หรือศาลาประชาคมใกล้บ้าน

ควรนำบัตรประชาชน ยาประจำตัว และของใช้จำเป็นติดตัวไป"""

            elif user_text == "7":
                reply_text = """📊 ตรวจสอบระดับน้ำ

ระบบต้นแบบยังไม่ได้เชื่อมข้อมูลระดับน้ำจริง

แนะนำให้ตรวจสอบจาก:
1. ปภ. โทร 1784
2. กรมอุตุนิยมวิทยา
3. เทศบาล / อบต.
4. ประกาศจากเจ้าหน้าที่ในพื้นที่"""

            elif user_text == "8" or user_text.upper().startswith("SOS"):
                loc = user_locations.get(event.source.user_id)

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
- ไฟดูดช่วงน้ำท่วมป้องกันยังไง
- หลังน้ำลดต้องทำอะไร"""

            else:
                reply_text = ask_ai(user_text)

        else:
            reply_text = "ขออภัย ระบบรองรับเฉพาะข้อความและพิกัด Location"

    except Exception as e:
        print("SYSTEM ERROR:", str(e))
        reply_text = "ขออภัย ระบบขัดข้องชั่วคราว กรุณาลองใหม่อีกครั้ง"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text[:4500])
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
