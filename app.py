import os
from flask import Flask, request

from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage, TextMessage
from linebot.models.events import MessageEvent
from linebot.exceptions import InvalidSignatureError

import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = os.getenv("MODEL", "gemini-2.5-flash")

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

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

def quick_menu():
    return """🌊 FLOODCARE AI เมนูช่วยเหลือน้ำท่วม

พิมพ์หมายเลขหรือคำสั่งที่ต้องการ

1️⃣ เตรียมตัวก่อนน้ำท่วม
2️⃣ วิธีอพยพเมื่อน้ำท่วม
3️⃣ ชุดยังชีพฉุกเฉิน
4️⃣ เบอร์ฉุกเฉิน
5️⃣ ปฐมพยาบาลเบื้องต้น
6️⃣ ถาม AI เรื่องน้ำท่วม"""

def flood_advice():
    return """🌊 เตรียมตัวก่อนน้ำท่วม

1. ติดตามข่าวจาก ปภ. กรมอุตุนิยมวิทยา และหน่วยงานท้องถิ่น
2. ยกของใช้ไฟฟ้า เอกสารสำคัญ และของมีค่าขึ้นที่สูง
3. เตรียมน้ำดื่ม อาหารแห้ง ยาประจำตัว ไฟฉาย และ power bank
4. ทำความสะอาดท่อระบายน้ำรอบบ้าน
5. วางแผนเส้นทางอพยพและจุดนัดพบของครอบครัว
6. เตรียมดูแลเด็ก ผู้สูงอายุ ผู้ป่วย และสัตว์เลี้ยง"""

def evacuation_route():
    return """🚶 วิธีอพยพเมื่อน้ำท่วม

1. ปฏิบัติตามคำสั่งเจ้าหน้าที่ทันที
2. ปิดสวิตช์ไฟหลัก ปิดแก๊ส และล็อกบ้านก่อนออก
3. นำเอกสารสำคัญ ยา น้ำดื่ม และโทรศัพท์ติดตัว
4. หลีกเลี่ยงการเดินลุยน้ำเชี่ยวหรือน้ำลึก
5. ห้ามแตะสายไฟ เสาไฟ หรืออุปกรณ์ไฟฟ้าที่อยู่ใกล้น้ำ
6. ไปยังพื้นที่สูง ศูนย์พักพิง หรือจุดปลอดภัย
7. แจ้งญาติหรือเจ้าหน้าที่เมื่อถึงที่ปลอดภัย"""

def emergency_kit():
    return """🎒 ชุดยังชีพฉุกเฉินควรมี

1. น้ำดื่มและอาหารแห้ง
2. ยาประจำตัวและยาสามัญ
3. ไฟฉาย ถ่านไฟฉาย และ power bank
4. เอกสารสำคัญใส่ถุงกันน้ำ
5. เงินสด
6. เสื้อผ้า ผ้าเช็ดตัว และของใช้ส่วนตัว
7. นกหวีดสำหรับขอความช่วยเหลือ
8. อุปกรณ์สำหรับเด็ก ผู้สูงอายุ หรือสัตว์เลี้ยง"""

def emergency_numbers():
    return """🚨 เบอร์ฉุกเฉิน

191 ตำรวจ
1669 การแพทย์ฉุกเฉิน
1784 กรมป้องกันและบรรเทาสาธารณภัย
199 ดับเพลิง
1146 กรมทางหลวง
1193 ตำรวจทางหลวง

หากอยู่ในอันตราย ให้โทรขอความช่วยเหลือทันที"""

def first_aid():
    return """🩹 ปฐมพยาบาลเบื้องต้นช่วงน้ำท่วม

1. หากมีบาดแผล ให้ล้างด้วยน้ำสะอาดและปิดแผล
2. หลีกเลี่ยงการแช่น้ำนาน เพราะเสี่ยงติดเชื้อ
3. หากถูกไฟฟ้าดูด ห้ามจับตัวผู้ป่วยโดยตรง ให้ตัดไฟก่อน
4. หากจมน้ำ ให้รีบแจ้ง 1669 และช่วยเหลือตามความปลอดภัย
5. หากมีไข้ ท้องเสีย หรือแผลบวมแดง ควรพบแพทย์"""

def ask_gemini(user_text):
    model = genai.GenerativeModel(MODEL)

    prompt = f"""
คุณคือ FLOODCARE AI ผู้ช่วยอัจฉริยะด้านน้ำท่วมและอุทกภัย

หน้าที่ของคุณ:
- ให้คำแนะนำก่อนน้ำท่วม ระหว่างน้ำท่วม และหลังน้ำลด
- แนะนำการอพยพอย่างปลอดภัย
- แนะนำชุดยังชีพฉุกเฉิน
- แนะนำการปฐมพยาบาลเบื้องต้น
- ตอบเป็นภาษาไทย
- ใช้ภาษาง่าย
- ตอบเป็นข้อ ๆ
- เน้นความปลอดภัยของประชาชน

คำถามของผู้ใช้:
{user_text}
"""

    response = model.generate_content(prompt)
    reply_text = response.text or "ขออภัย ระบบไม่สามารถสร้างคำตอบได้"
    return reply_text[:4500]

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text.strip()

    try:
        if user_text in ["เมนู", "menu", "Menu", "MENU"]:
            reply_text = quick_menu()

        elif user_text in ["1", "เตรียมตัวก่อนน้ำท่วม", "ก่อนน้ำท่วม"]:
            reply_text = flood_advice()

        elif user_text in ["2", "วิธีอพยพ", "อพยพ", "ต้องอพยพยังไง"]:
            reply_text = evacuation_route()

        elif user_text in ["3", "ชุดยังชีพ", "ถุงยังชีพ", "ของจำเป็น"]:
            reply_text = emergency_kit()

        elif user_text in ["4", "เบอร์ฉุกเฉิน", "สายด่วน", "ขอเบอร์ฉุกเฉิน"]:
            reply_text = emergency_numbers()

        elif user_text in ["5", "ปฐมพยาบาล", "การปฐมพยาบาล"]:
            reply_text = first_aid()

        else:
            reply_text = ask_gemini(user_text)

    except Exception as e:
        print("SYSTEM ERROR:", str(e))
        reply_text = "ขออภัย ระบบขัดข้องชั่วคราว กรุณาลองใหม่อีกครั้ง"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text[:4500])
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
