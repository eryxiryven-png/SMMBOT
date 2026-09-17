import sqlite3
import telebot
from telebot import types
from flask import Flask
from threading import Thread

API_TOKEN = "8761302883:AAGGgeUVSjQkuucXQXdJHtPHz-Gw2HQ9dT8"
ADMIN_ID = 8764166382

bot = telebot.TeleBot(API_TOKEN)

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect('smm_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            balance REAL DEFAULT 0.0,
            spent REAL DEFAULT 0.0,
            total_orders INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_user(user_id, username="", first_name=""):
    conn = sqlite3.connect('smm_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute('INSERT INTO users (user_id, username, first_name) VALUES (?, ?, ?)',
                       (user_id, username, first_name))
        conn.commit()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
    conn.close()
    return user

def update_balance(user_id, amount):
    conn = sqlite3.connect('smm_database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
    conn.commit()
    conn.close()

def deduct_balance_and_add_order(user_id, amount):
    conn = sqlite3.connect('smm_database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance = balance - ?, spent = spent + ?, total_orders = total_orders + 1 WHERE user_id = ?',
                   (amount, amount, user_id))
    conn.commit()
    conn.close()

# --- 24/7 Render Keep-Alive Server ---
app = Flask(__name__)

@app.route('/')
def home():
    return "SMM Bot is Running 24/7!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- Price List Data (Per 1000 Item / Unit Rate) ---
PRICES = {
    # TikTok
    "🎵 TikTok Like": {"rate": 0.04, "unit": "Like", "min": 100},
    "🎵 TikTok Views": {"rate": 0.003, "unit": "Views", "min": 1000},
    "🎵 TikTok Follower": {"rate": 0.20, "unit": "Follower", "min": 100},
    
    # Facebook
    "🔵 FB Page Follower": {"rate": 0.06, "unit": "Follower", "min": 100},
    "🔵 FB ID Follower": {"rate": 0.06, "unit": "Follower", "min": 100},
    "🔵 FB Post Like": {"rate": 0.075, "unit": "Like", "min": 100},
    "🔵 FB Post React": {"rate": 0.075, "unit": "React", "min": 100},
    "🔵 FB Video Views": {"rate": 0.02, "unit": "Views", "min": 1000},
    
    # Instagram
    "📷 IG Follower": {"rate": 0.15, "unit": "Follower", "min": 100},
    "📷 IG Like": {"rate": 0.04, "unit": "Like", "min": 100},
    "📷 IG Views": {"rate": 0.001, "unit": "Views", "min": 1000},
    
    # YouTube
    "🎥 YT Subscribe": {"rate": 0.19, "unit": "Subscriber", "min": 100},
    "🎥 YT Like": {"rate": 0.05, "unit": "Like", "min": 100},
    "🎥 YT Views": {"rate": 0.13, "unit": "Views", "min": 1000},
    "🎥 YT Watch Time": {"rate": 0.80, "unit": "Hours", "min": 100}
}

user_states = {}

# --- Keyboards ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("🟢 Buy Service"),
        types.KeyboardButton("💰 Deposit"),
        types.KeyboardButton("📜 Service Price"),
        types.KeyboardButton("👤 My Profile"),
        types.KeyboardButton("📞 Support")
    )
    return markup

def platforms_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("🎵 TikTok"),
        types.KeyboardButton("🔵 Facebook"),
        types.KeyboardButton("📷 Instagram"),
        types.KeyboardButton("🎥 YouTube"),
        types.KeyboardButton("🔙 মেইন মেনু")
    )
    return markup

def sub_services_menu(platform):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    if platform == "🎵 TikTok":
        markup.add("🎵 TikTok Like", "🎵 TikTok Views", "🎵 TikTok Follower")
    elif platform == "🔵 Facebook":
        markup.add("🔵 FB Page Follower", "🔵 FB ID Follower", "🔵 FB Post Like", "🔵 FB Post React", "🔵 FB Video Views")
    elif platform == "📷 Instagram":
        markup.add("📷 IG Follower", "📷 IG Like", "📷 IG Views")
    elif platform == "🎥 YouTube":
        markup.add("🎥 YT Subscribe", "🎥 YT Like", "🎥 YT Views", "🎥 YT Watch Time")
    markup.add("🔙 ব্যাক করুন")
    return markup

# --- Handlers ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    get_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    inline_kb = types.InlineKeyboardMarkup()
    inline_kb.add(types.InlineKeyboardButton("🚀 Join Channel", url="https://t.me/JUSTTRUSTBR0"))
    inline_kb.add(types.InlineKeyboardButton("👥 Join Group", url="https://t.me/buyselgroup0"))
    inline_kb.add(types.InlineKeyboardButton("⚡ Verify Membership", callback_data="verify"))

    welcome_text = (
        "👑 **WELCOME TO SERVICE MASTER** ⚡\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "বটটি ব্যবহার করতে নিচের চ্যানেল ও গ্রুপে অবশ্যই জয়েন করুন।\n"
        "📢 অফিসিয়াল চ্যানেল: @JUSTTRUSTBR0\n"
        "💬 অফিসিয়াল গ্রুপ: @buyselgroup0\n\n"
        "🟢 জয়েন শেষ হলে নিচে Verify বাটনে ক্লিক করুন!"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=inline_kb)

@bot.callback_query_handler(func=lambda call: call.data == "verify")
def verify_cb(call):
    user = get_user(call.from_user.id, call.from_user.username, call.from_user.first_name)
    bot.answer_callback_query(call.id, "✅ Account Verified Successfully!")
    dash_text = (
        "🌟 **SERVICE MASTER DASHBOARD** 🌟\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **ইউজার:** {user[2]}\n"
        f"💰 **ব্যালেন্স:** {user[3]:.2f} TK\n"
        f"📊 **মোট খরচ:** {user[4]:.2f} TK\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "নিচের বাটন থেকে সার্ভিস অর্ডার করুন:"
    )
    bot.send_message(call.message.chat.id, dash_text, parse_mode="Markdown", reply_markup=main_menu())

# --- Admin Commands ---
@bot.message_handler(commands=['addbalance'])
def add_bal_admin(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        args = message.text.split()
        target_id = int(args[1])
        amount = float(args[2])
        update_balance(target_id, amount)
        bot.reply_to(message, f"✅ Successfully added {amount} TK to User ID: `{target_id}`", parse_mode="Markdown")
        bot.send_message(target_id, f"🎉 **অ্যাডমিন আপনার অ্যাকাউন্টে {amount} টাকা যুক্ত করেছেন!**", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, "❌ Format Invalid!\nUse: `/addbalance <user_id> <amount>`")

@bot.message_handler(commands=['broadcast'])
def broadcast_admin(message):
    if message.from_user.id != ADMIN_ID:
        return
    msg_to_send = message.text.replace("/broadcast", "").strip()
    if not msg_to_send:
        bot.reply_to(message, "❌ বার্তা লিখুন! Use: `/broadcast <your_text>`")
        return
    
    conn = sqlite3.connect('smm_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    users = cursor.fetchall()
    conn.close()

    count = 0
    for u in users:
        try:
            bot.send_message(u[0], f"📢 **ADMIN ANNOUNCEMENT**\n\n{msg_to_send}", parse_mode="Markdown")
            count += 1
        except:
            pass
    bot.reply_to(message, f"✅ Broadcast sent to {count} users.")

# --- Text Handler ---
@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    text = message.text
    chat_id = message.chat.id
    user_id = message.from_user.id
    user = get_user(user_id, message.from_user.username, message.from_user.first_name)

    if text == "🟢 Buy Service":
        bot.send_message(chat_id, "🛒 **সার্ভিস মেনু ওপেন হয়েছে**\n\nনিচের কিবোর্ড থেকে প্ল্যাটফর্ম সিলেক্ট করুন:", reply_markup=platforms_menu())

    elif text in ["🎵 TikTok", "🔵 Facebook", "📷 Instagram", "🎥 YouTube"]:
        bot.send_message(chat_id, f"👉 **{text} এর সার্ভিসসমূহ:**\n\nআপনার কাঙ্খিত সার্ভিসটি বেছে নিন:", reply_markup=sub_services_menu(text))

    elif text in PRICES:
        service_data = PRICES[text]
        user_states[user_id] = {"service": text, "step": "quantity"}
        bot.send_message(
            chat_id,
            f"🎯 **{text}**\n"
            f"💰 প্রতি ১০০০ পরিমাণ = {service_data['rate'] * 1000:.2f} TK\n"
            f"⚠️ সর্বনিম্ন অর্ডার = {service_data['min']}\n\n"
            f"🔢 **আপনি কতগুলো নিতে চান? (শুধু সংখ্যা লিখুন):**"
        )

    elif text == "👤 My Profile":
        profile_text = (
            "👤 **USER ACCOUNT DETAILS** 👤\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"📛 **নাম:** {user[2]}\n"
            f"🆔 **আইডি:** `{user[0]}`\n"
            f"🔗 **ইউজার:** @{user[1]}\n\n"
            f"💰 **ব্যালেন্স:** {user[3]:.2f} TK\n"
            f"💸 **মোট খরচ:** {user[4]:.2f} TK\n"
            f"📦 **মোট অর্ডার:** {user[5]} টি\n"
            "📊 **স্ট্যাটাস:** Verified ✅"
        )
        bot.send_message(chat_id, profile_text, parse_mode="Markdown")

    elif text == "📜 Service Price":
        price_list = (
            "💬 **SOCIAL MEDIA ALL SERVICE LIST** 💬\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "💥 **টেলিগ্রাম লিস্ট** 👇\n"
            "🔹 1K Member = 30 TK (NoRefill)\n"
            "🔹 1K Lifetime Member = 160 TK\n"
            "🔹 Post View 1K = 3 TK\n"
            "🔹 Post React 1K = 10 TK\n\n"
            "💥 **টিকটক** 👇\n"
            "🔹 1K Like = 40 TK | 10K View = 30 TK | 1K Follower = 200 TK\n\n"
            "💥 **ফেসবুক** 👇\n"
            "🔹 1K Follower = 60 TK | 1K React = 75 TK | 1K Video View = 20 TK\n\n"
            "💥 **ইউটিউব** 👇\n"
            "🔹 1K Sub = 190 TK | 1K View = 130 TK | 1K Like = 50 TK\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🎁 সর্বনিম্ন অর্ডারে সুবিধা প্রযোজ্য।"
        )
        bot.send_message(chat_id, price_list, parse_mode="Markdown")

    elif text == "💰 Deposit":
        bot.send_message(chat_id, f"💰 **ডিপোজিট সিস্টেম**\n\nআপনার ID: `{user_id}`\n\nটাকা ডিপোজিট করতে অ্যাডমিনকে মেসেজ দিন:\nঅ্যাডমিন আইডি: @justtrustbro", parse_mode="Markdown")

    elif text == "📞 Support":
        inline_sup = types.InlineKeyboardMarkup()
        inline_sup.add(types.InlineKeyboardButton("💬 অ্যাডমিনের সাথে কথা বলুন", url="https://t.me/justtrustbro"))
        bot.send_message(chat_id, "📞 **সাপোর্ট সেন্টার**\nযেকোনো প্রয়োজনে সরাসরি অ্যাডমিনকে মেসেজ দিন।", reply_markup=inline_sup)

    elif text in ["🔙 মেইন মেনু", "🔙 ব্যাক করুন"]:
        bot.send_message(chat_id, "🏠 **মেইন মেনু**", reply_markup=main_menu())

    # Order Input Processing Step
    elif user_id in user_states:
        state = user_states[user_id]
        
        if state["step"] == "quantity":
            if not text.isdigit():
                bot.send_message(chat_id, "❌ **দয়া করে শুধু সঠিক সংখ্যা লিখুন!**")
                return
            qty = int(text)
            service_name = state["service"]
            min_req = PRICES[service_name]["min"]

            if qty < min_req:
                bot.send_message(chat_id, f"⚠️ **সর্বনিম্ন {min_req} টি অর্ডার করতে হবে!**")
                return

            cost = qty * PRICES[service_name]["rate"]
            if user[3] < cost:
                bot.send_message(chat_id, f"❌ **পর্যাপ্ত ব্যালেন্স নেই!**\n\nমোট লাগবে: {cost:.2f} TK\nআপনার ব্যালেন্স: {user[3]:.2f} TK\n\nডিপোজিট করতে `💰 Deposit` অপশনে যান।")
                user_states.pop(user_id, None)
                return

            state["quantity"] = qty
            state["cost"] = cost
            state["step"] = "link"
            bot.send_message(chat_id, f"🔗 **মোট খরচ:** {cost:.2f} TK\n\n**এখন আপনার পোস্ট/প্রোফাইল লিংকটি দিন:**")

        elif state["step"] == "link":
            link = text
            qty = state["quantity"]
            cost = state["cost"]
            service_name = state["service"]

            # Deduct Balance
            deduct_balance_and_add_order(user_id, cost)

            # Confirm User
            bot.send_message(chat_id, f"✅ **আপনার অর্ডার সফলভাবে সাবমিট হয়েছে!**\n\n📦 **সার্ভিস:** {service_name}\n🔢 **পরিমাণ:** {qty}\n💰 **মোট খরচ:** {cost:.2f} TK\n🔗 **লিংক:** {link}", reply_markup=main_menu())

            # Notify Admin
            admin_notice = (
                "🚨 **NEW SMM ORDER RECEIVED** 🚨\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 **ইউজার:** {user[2]} (@{user[1]})\n"
                f"🆔 **ইউজার আইডি:** `{user_id}`\n"
                f"📦 **সার্ভিস:** {service_name}\n"
                f"🔢 **পরিমাণ:** {qty}\n"
                f"💰 **কাটা ব্যালেন্স:** {cost:.2f} TK\n"
                f"🔗 **লিংক:** `{link}`"
            )
            bot.send_message(ADMIN_ID, admin_notice, parse_mode="Markdown")
            user_states.pop(user_id, None)

if __name__ == '__main__':
    keep_alive()
    print("Bot starting...")
    bot.infinity_polling()
