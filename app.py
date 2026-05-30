import os
import gspread
from flask import Flask, request
from oauth2client.service_account import ServiceAccountCredentials

from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage, TextMessage, LocationMessage, MessageEvent
from linebot.exceptions import InvalidSignatureError

import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = os.getenv("MODEL", "gemini-2.5-flash")

app = Flask(__name__)

# LINE Bot
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# Google Sheet setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_file = os.getenv("GS_CREDENTIALS_JSON")  # Service account JSON
creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
client = gspread.authorize(creds)
sheet = client.open("Floodcare_SOS").sheet1

# Store user locations temporarily
user_locations = {}

# Menu text
menu_text = (
    "🌊 FLOODCARE AI 3.0 เมนูช่วยเหลือน้ำท่วม\n"
    "พิมพ์หมายเลขที่ต้องการ:\n"
    "1️⃣ เตรียมตัวก่อนน้ำท่วม\n"
    "2️⃣ วิธีอพยพเมื่อน้ำท่วม\n"
    "3️⃣ ชุดยังชีพฉุกเฉิน\n"
    "4️⃣ เบอร์ฉุกเฉิน\n"
    "5️⃣ ปฐมพยาบาลเบื้องต้น\n"
    "6️⃣ ศูนย์พักพิง\n"
    "7️⃣ ตรวจสอบระดับน้ำ\n"
    "8️⃣ SOS ขอความช่วยเหลือ\n"
    "9️⃣ ถาม AI เรื่องน้ำท่วม"
)

# Predefined menu responses 1–7
menu_responses = {
    "1": "1️⃣ เตรียมตัวก่อนน้ำท่วม:\n- ติดตามข่าวสาร\n- ยกของขึ้นที่สูง\n- เตรียมถุงยังชีพ\n- ทำความสะอาดท่อระบายน้ำ\n- เตรียมกระสอบทราย",
    "2": "2️⃣ วิธีอพยพเมื่อน้ำท่วม:\n- ปฏิบัติตามคำสั่งอพยพ\n- สวมเสื้อผ้าเหมาะสม\n- เดินทางตามเส้นทางที่กำหนด\n- ระวังไฟฟ้าและของมีคม",
    "3": "3️⃣ ชุดยังชีพฉุกเฉิน:\n- น้ำดื่ม, อาหารแห้ง, ยารักษาโรค, ไฟฉาย, วิทยุ, เอกสารสำคัญ, เงินสด, เสื้อผ้า, power bank",
    "4": "4️⃣ เบอร์ฉุกเฉิน:\n- 191 ตำรวจ\n- 199 สาธารณภัย\n- 1669 โรงพยาบาล\n- 1784 ปภ.",
    "5": "5️⃣ ปฐมพยาบาลเบื้องต้น:\n- ทำแผล, ให้ยาแก้ปวด, ช่วยฟื้นคืนสติ, CPR, ปฐมพยาบาลเด็ก/ผู้สูงอายุ",
    "6": "6️⃣ ศูนย์พักพิง:\n- ศูนย์อพยพในพื้นที่ใกล้เคียง\n- เตรียมอาหาร, น้ำดื่ม, ที่นอน, ยาสามัญ\n- ปฏิบัติตามกฎของศูนย์พักพิง",
    "7": "7️⃣ ตรวจสอบระดับน้ำ:\n- ใช้แอป, เว็บไซต์ราชการ, กล้อง CCTV, ข้อมูลผู้เชี่ยวชาญ"
}

# Handle LINE messages
@handler.add(MessageEvent)
def handle_message(event):
    try:
        # Location message
        if isinstance(event.message, LocationMessage):
            user_locations[event.source.user_id] = (event.message.latitude, event.message.longitude)
            reply_text = "📍 ได้รับพิกัดแล้ว พิมพ์ SOS เพื่อขอความช่วยเหลือ"

        # Text message
        elif isinstance(event.message, TextMessage):
            text = event.message.text.strip()
            
            # Menu
            if text.lower() == "เมนู":
                reply_text = menu_text
            
            # SOS
            elif text.upper() == "SOS" or text == "8":
                user_id = event.source.user_id
                lat, lng = user_locations.get(user_id, ("ไม่ระบุ", "ไม่ระบุ"))
                sheet.append_row(["รอกรอกชื่อ", "รอกรอกเบอร์", lat, lng, "รอระดับน้ำ", "รอคำขอความช่วยเหลือ"])
                reply_text = f"📌 SOS ได้ถูกบันทึกแล้ว\nพิกัด: {lat}, {lng}"
            
            # Predefined menu 1–7
            elif text in menu_responses:
                reply_text = menu_responses[text]

            # AI questions (menu 9)
            else:
                try:
                    model = genai.GenerativeModel(MODEL)
                    response = model.generate_content(text)
                    reply_text = response.text[:4500] or "ขออภัย ระบบไม่สามารถสร้างคำตอบได้"
                except Exception as e:
                    print("GEMINI ERROR:", str(e))
                    reply_text = "ขออภัย ระบบ AI ขัดข้องชั่วคราว กรุณาลองใหม่อีกครั้ง"
        
        # Reply
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
    except Exception as e:
        print("Error:", e)

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
