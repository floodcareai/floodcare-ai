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
    return "FLOODCARE AI 2.0 is running"


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
    return """🌊 FLOODCARE AI 2.0

พิมพ์หมายเลขหรือคำสั่งที่ต้องการ

1️⃣ เตรียมตัวก่อนน้ำท่วม
2️⃣ วิธีอพยพเมื่อน้ำท่วม
3️⃣ ชุดยังชีพฉุกเฉิน
4️⃣ เบอร์ฉุกเฉิน
5️⃣ ปฐมพยาบาลเบื้องต้น
6️⃣ ศูนย์พักพิง
7️⃣ ตรวจสอบระดับน้ำ
8️⃣ SOS ขอความช่วยเหลือ
9️⃣ ถาม AI เรื่องน้ำท่วม

ตัวอย่าง:
- เมนู
- เบอร์ฉุกเฉิน
- SOS
- ระดับน้ำ
- ศูนย์พักพิง"""


def flood_advice():
    return """🌊 เตรียมตัวก่อนน้ำท่วม

1. ติดตามข่าวจาก ปภ. กรมอุตุนิยมวิทยา และหน่วยงานท้องถิ่น
2. ยกเครื่องใช้ไฟฟ้า เอกสารสำคัญ และของมีค่าขึ้นที่สูง
3. เตรียมน้ำดื่ม อาหารแห้ง ยาประจำตัว ไฟฉาย และ power bank
4. ทำความสะอาดท่อระบายน้ำรอบบ้าน
5. เตรียมกระสอบทรายหากอยู่พื้นที่เสี่ยง
6. วางแผนเส้นทางอพยพและจุดนัดพบของครอบครัว
7. เตรียมดูแลเด็ก ผู้สูงอายุ ผู้ป่วย และสัตว์เลี้ยง"""


def evacuation_route():
    return """🚶 วิธีอพยพเมื่อน้ำท่วม

1. ปฏิบัติตามคำสั่งเจ้าหน้าที่ทันที
2. ปิดสวิตช์ไฟหลัก ปิดแก๊ส และล็อกบ้านก่อนออก
3. นำเอกสารสำคัญ ยา น้ำดื่ม โทรศัพท์ และ power bank ติดตัว
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
8. หน้ากากอนามัย เจลล้างมือ และถุงขยะ
9. อุปกรณ์สำหรับเด็ก ผู้สูงอายุ หรือสัตว์เลี้ยง"""


def emergency_numbers():
    return """🚨 เบอร์ฉุกเฉิน

191 ตำรวจ
1669 การแพทย์ฉุกเฉิน
1784 กรมป้องกันและบรรเทาสาธารณภัย
199 ดับเพลิง
1146 กรมทางหลวง
1193 ตำรวจทางหลวง
1667 สายด่วนสุขภาพจิต

หากอยู่ในอันตราย ให้โทรขอความช่วยเหลือทันที"""


def first_aid():
    return """🩹 ปฐมพยาบาลเบื้องต้นช่วงน้ำท่วม

1. หากมีบาดแผล ให้ล้างด้วยน้ำสะอาดและปิดแผล
2. หลีกเลี่ยงการแช่น้ำนาน เพราะเสี่ยงติดเชื้อ
3. หากถูกไฟฟ้าดูด ห้ามจับตัวผู้ป่วยโดยตรง ให้ตัดไฟก่อน
4. หากจมน้ำ ให้รีบโทร 1669 และช่วยเหลือตามความปลอดภัย
5. หากมีไข้ ท้องเสีย หรือแผลบวมแดง ควรพบแพทย์
6. ล้างมือบ่อย ๆ และหลีกเลี่ยงน้ำสกปรก"""


def shelter_info():
    return """🏠 ศูนย์พักพิง

หากต้องการศูนย์พักพิงใกล้บ้าน ให้ติดต่อหน่วยงานท้องถิ่น

ช่องทางแนะนำ:
1. อบต. / เทศบาลในพื้นที่
2. ผู้ใหญ่บ้าน / กำนัน
3. ปภ. โทร 1784
4. โรงเรียน วัด หรือศาลาประชาคมที่เปิดเป็นศูนย์พักพิง

กรุณาเตรียม:
- บัตรประชาชน
- ยาประจำตัว
- เสื้อผ้า
- อาหารเด็กหรือของใช้ผู้สูงอายุ หากมี"""


def water_level():
    return """📊 ตรวจสอบระดับน้ำ

ขณะนี้ระบบต้นแบบยังไม่ได้เชื่อมต่อข้อมูลระดับน้ำแบบเรียลไทม์

คำแนะนำ:
1. ติดตามประกาศจาก ปภ. โทร 1784
2. ตรวจสอบข่าวจากกรมอุตุนิยมวิทยา
3. ติดตามประกาศจากเทศบาลหรือ อบต.
4. หากน้ำเพิ่มเร็ว ให้ย้ายของขึ้นที่สูงและเตรียมอพยพทันที

สถานะระบบ:
🟡 โหมดต้นแบบ
สามารถต่อยอดเชื่อม API ระดับน้ำจริงได้ในอนาคต"""


def sos_help():
    return """🚨 SOS ขอความช่วยเหลือ

โปรดส่งข้อมูลตามรูปแบบนี้:

SOS
ชื่อ:
เบอร์โทร:
ที่อยู่/จุดสังเกต:
จำนวนผู้ประสบภัย:
มีเด็ก/ผู้สูงอายุ/ผู้ป่วยหรือไม่:
ระดับน้ำโดยประมาณ:
ต้องการความช่วยเหลือ:

ตัวอย่าง:
SOS
ชื่อ: สมชาย
เบอร์โทร: 08x-xxx-xxxx
ที่อยู่: หมู่ 3 ใกล้วัด...
จำนวนผู้ประสบภัย: 4 คน
มีผู้สูงอายุ 1 คน
ระดับน้ำ: ประมาณเอว
ต้องการเรืออพยพ

หากฉุกเฉินมาก โทร 191, 1669 หรือ 1784 ทันที"""


def ask_gemini(user_text):
    model = genai.GenerativeModel(MODEL)

    prompt = f"""
คุณคือ FLOODCARE AI 2.0 ผู้ช่วยอัจฉริยะด้านน้ำท่วมและอุทกภัย

หน้าที่ของคุณ:
- ให้คำแนะนำก่อนน้ำท่วม ระหว่างน้ำท่วม และหลังน้ำลด
- แนะนำการอพยพอย่างปลอดภัย
- แนะนำชุดยังชีพฉุกเฉิน
- แนะนำเบอร์ฉุกเฉินที่เกี่ยวข้อง
- แนะนำการปฐมพยาบาลเบื้องต้น
- แนะนำการติดต่อศูนย์พักพิงและเจ้าหน้าที่
- หากเป็นเหตุฉุกเฉิน ให้แนะนำให้โทร 191, 1669 หรือ 1784 ทันที

รูปแบบคำตอบ:
- ตอบเป็นภาษาไทย
- ใช้ภาษาง่าย
- ตอบเป็นข้อ ๆ
- กระชับ แต่ครบถ้วน
- เน้นความปลอดภัยของประชาชน
- ห้ามแต่งข้อมูลระดับน้ำจริงหากไม่มีข้อมูล
- ถ้าไม่แน่ใจ ให้แนะนำให้ติดต่อหน่วยงานราชการหรือเจ้าหน้าที่ท้องถิ่น

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

        elif user_text in ["6", "ศูนย์พักพิง", "ที่พักพิง", "ศูนย์อพยพ"]:
            reply_text = shelter_info()

        elif user_text in ["7", "ระดับน้ำ", "ตรวจสอบระดับน้ำ", "น้ำสูงไหม"]:
            reply_text = water_level()

        elif user_text.upper().startswith("SOS") or user_text in ["8", "ขอความช่วยเหลือ", "ช่วยด้วย"]:
            reply_text = sos_help()

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
