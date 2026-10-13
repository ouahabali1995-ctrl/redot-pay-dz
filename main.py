import telebot
from telebot import types
import sqlite3
import time
import os
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# ================= Configuration =================
BOT_TOKEN = "8826585633:AAEqNS0ZF46M1MDsrnHY-R8Ww5FYS3mAj6k"
REFERRAL_URL = "https://url.hk/i/en/tgpvf"
ADMIN_ID = 7523972119
ADMIN_USERNAME = "alaeddine8"
CHANNEL_LINK = "https://t.me/BaridMoaqat"
DB_FILE = os.path.join(os.path.dirname(__file__), "redotpay_bot.db")
EXCHANGE_RATE = 245

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ================= WSGI Web App for Gunicorn =================
def app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/html; charset=utf-8')]
    start_response(status, response_headers)
    return ["<h1>بوت ريدوت باي الجزائر يعمل بنجاح 24/7 💳🇩🇿</h1>".encode('utf-8')]

# Start bot polling in background thread (runs whether under gunicorn or standalone)
def run_bot_polling():
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=20)
        except Exception:
            time.sleep(5)

polling_thread = threading.Thread(target=run_bot_polling, daemon=True)
polling_thread.start()

# Standalone HTTP Server (only used if running python main.py directly)
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write("<h1>بوت ريدوت باي الجزائر يعمل بنجاح 24/7 💳🇩🇿</h1>".encode('utf-8'))

    def log_message(self, format, *args):
        pass

# ================= Database Setup =================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            username TEXT,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

def get_db():
    return sqlite3.connect(DB_FILE)

def safe_answer_callback(call_id, text=None, show_alert=False):
    try:
        bot.answer_callback_query(call_id, text=text, show_alert=show_alert)
    except Exception:
        pass

# ================= Keyboards =================
def get_main_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_ref = types.InlineKeyboardButton("🎁 سجل الآن واكسب 5$ هدية مجاناً", url=REFERRAL_URL)
    btn_contact = types.InlineKeyboardButton("💬 طلب شحن رصيد بالدينار (تواصل معي مباشرة)", url=f"https://t.me/{ADMIN_USERNAME}")
    btn_steps = types.InlineKeyboardButton("📖 طريقة التسجيل وتوثيق الهوية", callback_data="guide_signup")
    btn_cards = types.InlineKeyboardButton("💳 أسعار وأنواع البطاقات", callback_data="guide_cards")
    btn_deposit = types.InlineKeyboardButton("🔄 طريقة الشحن من بريدي موب", callback_data="guide_deposit")
    btn_calc = types.InlineKeyboardButton("📊 حاسبة سعر الصرف بالدينار", callback_data="open_calc")
    btn_channel = types.InlineKeyboardButton("📢 قناتنا الرسمية", url=CHANNEL_LINK)

    markup.row(btn_ref)
    markup.row(btn_contact)
    markup.row(btn_steps, btn_cards)
    markup.row(btn_deposit, btn_calc)
    markup.row(btn_channel)
    return markup

def get_back_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_ref = types.InlineKeyboardButton("🎁 سجل الآن واكسب 5$ هدية", url=REFERRAL_URL)
    btn_back = types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")
    markup.add(btn_ref, btn_back)
    return markup

# ================= Handlers =================
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "صديقي"
    username = message.from_user.username or ""

    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, first_name, username) VALUES (?, ?, ?)",
              (user_id, first_name, username))
    conn.commit()
    conn.close()

    welcome_text = (
        f"مرحباً بك يا <b>{first_name}</b> في بوت <b>دليل بطاقة ريدوت باي في الجزائر</b> 💳🇩🇿✨\n\n"
        "بوابتك لامتلاك بطاقة فيزا دولية للشراء من جميع مواقع الإنترنت، وتفعيل بايبال، وتلقي المدفوعات بأمان تام!\n\n"
        "🔥 <b>مميزات بطاقة ريدوت باي (RedotPay):</b>\n"
        "✅ مقبولة 100% في علي إكسبريس، فيسبوك آدز، نيتفليكس، جوجل بلاي وكل المنصات.\n"
        "✅ تفعيل بنك بايبال وسحب الأموال منه بسهولة.\n"
        "✅ توثيق فوري بالبطاقة البيومترية الجزائرية دون تعقيدات بنكية.\n"
        "✅ هدية ترحيبية بقيمة <b>5 دولارات</b> مجاناً في محفظتك عند التسجيل من الرابط أدناه!\n\n"
        "👇 <b>اختر ما تحتاجه من القائمة التفاعلية أدناه:</b>"
    )
    PHOTO_FILE = os.path.join(os.path.dirname(__file__), "logo.jpg")
    if os.path.exists(PHOTO_FILE):
        try:
            with open(PHOTO_FILE, "rb") as photo:
                bot.send_photo(message.chat.id, photo, caption=welcome_text, reply_markup=get_main_keyboard())
                return
        except Exception:
            pass
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard())

@bot.message_handler(commands=['admin'])
def handle_admin(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    conn.close()

    admin_text = (
        "👑 <b>لوحة تحكم المسؤول (ريدوت باي)</b>\n\n"
        f"👥 إجمالي المستخدمين المسجلين في البوت: <b>{total_users}</b>\n\n"
        "لإرسال إذاعة لجميع المشتركين، أرسل:\n"
        "<code>/broadcast نص_الرسالة_هنا</code>"
    )
    bot.send_message(message.chat.id, admin_text)

@bot.message_handler(commands=['broadcast'])
def handle_broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    text = message.text.replace("/broadcast", "").strip()
    if not text:
        bot.send_message(message.chat.id, "❌ يرجى كتابة نص الإذاعة بعد الأمر مباشرة.")
        return

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    users = c.fetchall()
    conn.close()

    sent_count = 0
    for (uid,) in users:
        try:
            bot.send_message(uid, f"📢 <b>إشعار رسمي:</b>\n\n{text}")
            sent_count += 1
            time.sleep(0.04)
        except Exception:
            pass

    bot.send_message(message.chat.id, f"✅ تم إرسال الإذاعة بنجاح إلى <b>{sent_count}</b> مستخدم.")

user_calc_state = {}

@bot.message_handler(func=lambda msg: user_calc_state.get(msg.from_user.id) == "waiting_calc_amount")
def handle_calc_input(message):
    user_id = message.from_user.id
    user_calc_state[user_id] = None
    
    try:
        amount = float(message.text.replace("$", "").replace("دج", "").strip())
        if amount <= 0:
            raise ValueError
        
        dzd_total = amount * EXCHANGE_RATE
        calc_res = (
            f"📊 <b>نتيجة حاسبة سعر الصرف التقريبي:</b>\n\n"
            f"💵 المبلغ بالدولار: <b>{amount:.2f} $</b>\n"
            f"🇩🇿 القيمة بالدينار الجزائري: <b>{dzd_total:,.0f} دج</b>\n"
            f"<i>(محسوبة على سعر الصرف التقريبي: 1 دولار = {EXCHANGE_RATE} دينار)</i>\n\n"
            "💡 لشحن هذا المبلغ في بطاقتك مباشرة عبر بريدي موب، تواصل مع المشرف."
        )
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_contact = types.InlineKeyboardButton("💬 تواصل مع المشرف للشحن", url=f"https://t.me/{ADMIN_USERNAME}")
        btn_back = types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")
        markup.add(btn_contact, btn_back)
        bot.send_message(message.chat.id, calc_res, reply_markup=markup)
    except Exception:
        bot.send_message(message.chat.id, "❌ يرجى إدخال رقم صحيح (مثال: 10 أو 50). أعد المحاولة من القائمة الرئيسية.",
                         reply_markup=get_back_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    user_id = call.from_user.id

    if call.data == "main_menu":
        safe_answer_callback(call.id)
        first_name = call.from_user.first_name or "صديقي"
        text = (
            f"أهلاً بك مجدداً يا <b>{first_name}</b> في <b>دليل ريدوت باي الجزائر</b> 💳🇩🇿\n\n"
            "احصل على بطاقتك واستفد من 5 دولارات مجاناً ترحيبية!\n"
            "اختر ما تريد من القائمة أدناه:"
        )
        try:
            bot.edit_message_text(text, chat_id, msg_id, reply_markup=get_main_keyboard())
        except Exception:
            bot.send_message(chat_id, text, reply_markup=get_main_keyboard())

    elif call.data == "guide_signup":
        safe_answer_callback(call.id)
        text = (
            "📖 <b>خطوات التسجيل وتوثيق الحساب بنجاح:</b>\n\n"
            "1️⃣ <b>التسجيل عبر الرابط:</b>\n"
            f"اضغط على زر التسجيل واحصل على هدية 5$ فورية:\n👉 <a href='{REFERRAL_URL}'>اضغط هنا للتسجيل مع هدية 5$</a>\n\n"
            "2️⃣ <b>تحميل التطبيق:</b>\n"
            "بعد التسجيل، حمل تطبيق RedotPay من متجر بلاي وسجل الدخول بنفس الإيميل.\n\n"
            "3️⃣ <b>توثيق الهوية (KYC):</b>\n"
            "🔹 ادخل لإعدادات الحساب واختر التحقق من الهوية.\n"
            "🔹 اختر بطاقة التعريف الوطنية البيومترية أو جواز السفر.\n"
            "🔹 صور البطاقة بوضوح تام بدون فلاش وبإضاءة جيدة.\n"
            "🔹 التقط صورة شخصية سيلفي سريعة.\n\n"
            "⏱️ <i>تتم مراجعة الحساب والموافقة عليه في أقل من 5 دقائق!</i>"
        )
        try:
            bot.edit_message_text(text, chat_id, msg_id, reply_markup=get_back_keyboard())
        except Exception:
            bot.send_message(chat_id, text, reply_markup=get_back_keyboard())

    elif call.data == "guide_cards":
        safe_answer_callback(call.id)
        text = (
            "💳 <b>أنواع بطاقات ريدوت باي وأسعارها:</b>\n\n"
            "1️⃣ <b>البطاقة الافتراضية (Virtual Card):</b>\n"
            "🔹 السعر الأصلي: 10 دولارات.\n"
            "🔹 لكن عند التسجيل برابطنا تحصل على <b>5 دولارات خصم هدية</b>، فتدفع 5$ فقط لطلبها!\n"
            "🔹 صالحة للشراء من كل المواقع، الإعلانات، وتفعيل البايبال فوراً.\n\n"
            "2️⃣ <b>البطاقة البلاستيكية الفعلية (Physical Card):</b>\n"
            "🔹 السعر: 100 دولار.\n"
            "🔹 يتم شحنها إلى عنوانك وتستخدم لسحب الأموال من الصراف الآلي والشراء من المحلات في الخارج.\n\n"
            "💡 <i>ننصحك بالبدء بالبطاقة الافتراضية فهي ممتازة وتفي بكل أغراض الشراء والتفعيل!</i>"
        )
        try:
            bot.edit_message_text(text, chat_id, msg_id, reply_markup=get_back_keyboard())
        except Exception:
            bot.send_message(chat_id, text, reply_markup=get_back_keyboard())

    elif call.data == "guide_deposit":
        safe_answer_callback(call.id)
        text = (
            "🔄 <b>طريقة شحن رصيد بطاقتك بالدينار من بريدي موب:</b>\n\n"
            "ريدوت باي تشحن عبر العملات الرقمية المستقرة (USDT):\n\n"
            "🔹 <b>الطريقة الأولى (بنفسك عبر بينانس P2P):</b>\n"
            "1. تفتح حساباً في منصة Binance.\n"
            "2. تدخل لقسم P2P وتشتري رصيد USDT بالدينار الجزائري عبر تطبيق بريدي موب.\n"
            "3. تحول الرصيد إلى محفظة RedotPay برسم بسيط عبر شبكة Binance Pay مجاناً!\n\n"
            "🔹 <b>الطريقة الثانية (الشحن المباشر السريع عبر المشرف):</b>\n"
            "إذا لم تكن تملك حساب بينانس وتريد شحن بطاقتك فوراً، يمكنك إرسال المبلغ بالدينار عبر بريدي موب للمشرف ويقوم بشحن حسابك في دقائق.\n\n"
            f"💬 اضغط على الزر أدناه لمراسلتي مباشرة للشحن:"
        )
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_ship = types.InlineKeyboardButton("💬 اضغط هنا لمراسلتي والشحن المباشر", url=f"https://t.me/{ADMIN_USERNAME}")
        btn_back = types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")
        markup.add(btn_ship, btn_back)
        try:
            bot.edit_message_text(text, chat_id, msg_id, reply_markup=markup)
        except Exception:
            bot.send_message(chat_id, text, reply_markup=markup)

    elif call.data == "open_calc":
        safe_answer_callback(call.id)
        user_calc_state[user_id] = "waiting_calc_amount"
        text = (
            "📊 <b>حاسبة سعر الصرف (الدولار مقابل الدينار الجزائري):</b>\n\n"
            f"سعر الصرف المعتمد حالياً هو تقريباً: <b>1 دولار = {EXCHANGE_RATE} دج</b>\n\n"
            "✍️ <b>أرسل الآن في رسالة المبلغ بالدولار الذي تريد معرفة قيمته بالدينار:</b>\n"
            "<i>(مثال: أرسل الرقم 10 أو 50 أو 100)</i>"
        )
        try:
            bot.edit_message_text(text, chat_id, msg_id, reply_markup=get_back_keyboard())
        except Exception:
            bot.send_message(chat_id, text, reply_markup=get_back_keyboard())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()
