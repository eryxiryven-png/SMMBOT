import sqlite3
import telebot
from telebot import types
from flask import Flask
from threading import Thread

API_TOKEN = "8761302883:AAGGgeUVSjQkuucXQXdJHtPHz-Gw2HQ9dT8"
SUPER_ADMIN_ID = 8764166382  # মূল মালিকের ID

bot = telebot.TeleBot(API_TOKEN)

# --- Database Management ---
def init_db():
    conn = sqlite3.connect('smm_panel.db')
    cursor = conn.cursor()
    # Users Table
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
    # Admins Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY
        )
    ''')
    # Settings Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    # Services & Pricing Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            service_key TEXT PRIMARY KEY,
            service_name TEXT,
            rate REAL,
            min_qty INTEGER
        )
    ''')
    
    # Super Admin Insertion
    cursor.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (SUPER_ADMIN_ID,))
    # Default Support Contact
    cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES ("support_contact", "justtrustbro")')

    # Default Services Initialization
    default_services = [
        # TikTok
        ("tiktok_like", "🎵 TikTok Like", 0.04, 100),
        ("tiktok_views", "🎵 TikTok Views", 0.003, 1000),
        ("tiktok_followers", "🎵 TikTok Follower", 0.20, 100),
        # Facebook
        ("fb_page_followers", "🔵 FB Page Follower", 0.06, 100),
        ("fb_id_followers", "🔵 FB ID Follower", 0.06, 100),
        ("fb_post_like", "🔵 FB Post Like", 0.075, 100),
        ("fb_post_react", "🔵 FB Post React", 0.075, 100),
        ("fb_video_views", "🔵 FB Video Views", 0.02, 1000),
        # Instagram
        ("ig_followers", "📷 IG Follower", 0.15, 100),
        ("ig_like", "📷 IG Like", 0.04, 100),
        ("ig_views", "📷 IG Views", 0.001, 1000),
        # YouTube
        ("yt_subscribe", "🎥 YT Subscribe", 0.19, 100),
        ("yt_like", "🎥 YT Like", 0.05, 100),
        ("yt_views", "🎥 YT Views", 0.13, 1000),
        ("yt_watchtime", "🎥 YT Watch Time", 0.80, 100)
    ]
    for s_key, s_name, rate, min_q in default_services:
        cursor.execute('INSERT OR IGNORE INTO services (service_key, service_name, rate, min_qty) VALUES (?, ?, ?, ?)',
                       (s_key, s_name, rate, min_q))
        
    conn.commit()
    conn.close()

init_db()

# --- Helper Functions ---
def is_admin(user_id):
    conn = sqlite3.connect('smm_panel.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM admins WHERE user_id = ?', (user_id,))
    res = cursor.fetchone()
    conn.close()
    return res is not None

def get_setting(key):
    conn = sqlite3.connect('smm_panel.db')
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else ""

def set_setting(key, value):
    conn = sqlite3.connect('smm_panel.db')
    cursor = conn.cursor()
    cursor.execute('REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
    conn.commit()
    conn.close()

def get_user(user_id, username="", first_name=""):
    conn = sqlite3.connect('smm_panel.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute('INSERT INTO users (user_id, username, first_name) VALUES (?, ?, ?)', (user_id, username, first_name))
        conn.commit()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
    conn.close()
    return user

def get_services():
    conn = sqlite3.connect('smm_panel.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM services')
    rows = cursor.fetchall()
    conn.close()
    services = {}
    for r in rows:
        services[r[1]] = {"key": r[0], "rate": r[2], "min": r[3]}
    return services

# --- 24/7 Render Keep-Alive ---
app = Flask(__name__)
@app.route('/')
def home():
    return "Pro SMM Panel Bot Active 24/7"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run_flask).start()

user_states = {}

# --- Keyboards ---
def main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("🟢 Buy Service"),
        types.KeyboardButton("💰 Deposit"),
        types.KeyboardButton("📜 Service Price"),
        types.KeyboardButton("👤 My Profile"),
        types.KeyboardButton("📞 Support")
    )
    if is_admin(user_id):
        markup.add(types.KeyboardButton("⚙️ Admin Control Panel"))
    return markup

def platforms_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("🎵 TikTok", "🔵 Facebook", "📷 Instagram", "🎥 YouTube", "🔙 মেইন মেনু")
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

def admin_panel_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💳 Add Balance", callback_data="adm_add_bal"),
        types.InlineKeyboardButton("🏷 Change Price", callback_data="adm_change_price"),
        types.InlineKeyboardButton("📞 Change Support ID", callback_data="adm_change_supp"),
        types.InlineKeyboardButton("👥 Add Admin", callback_data="adm_add_admin"),
        types.InlineKeyboardButton("🗑 Remove Admin", callback_data="adm_rem_admin"),
        types.InlineKeyboardButton("📢 Broadcast", callback_data="adm_broadcast")
    )
    return markup

# --- Handlers ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    get_user(user_id, message.from_user.username, message.from_user.first_name)
    
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

@bot.callback_query_handler(func=lambda call: call.data.startswith("verify"))
def verify_cb(call):
    user_id = call.from_user.id
    user = get_user(user_id, call.from_user.username, call.from_user.first_name)
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
    bot.send_message(call.message.chat.id, dash_text, parse_mode="Markdown", reply_markup=main_menu(user_id))

# --- Admin Panel Callback Handler ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_"))
def admin_callbacks(call):
    user_id = call.from_user.id
    if not is_admin(user_id):
        bot.answer_callback_query(call.id, "❌ আপনি অ্যাডমিন নন!", show_alert=True)
        return

    action = call.data

    if action == "adm_add_bal":
        user_states[user_id] = {"admin_action": "add_balance"}
        bot.send_message(call.message.chat.id, "💳 **ব্যালেন্স অ্যাড ফরম্যাট:**\nইউজার আইডি এবং পরিমাণ স্পেস দিয়ে লিখুন।\n\nউদাহরণ: `6587881288 100`", parse_mode="Markdown")

    elif action == "adm_change_supp":
        user_states[user_id] = {"admin_action": "change_support"}
        bot.send_message(call.message.chat.id, "📞 **নতুন সাপোর্ট ইউজারনেমটি লিখুন (@ ছাড়া):**\nউদাহরণ: `justtrustbro`")

    elif action == "adm_add_admin":
        user_states[user_id] = {"admin_action": "add_admin"}
        bot.send_message(call.message.chat.id, "👥 **নতুন অ্যাডমিনের Telegram User ID লিখুন:**")

    elif action == "adm_rem_admin":
        user_states[user_id] = {"admin_action": "remove_admin"}
        bot.send_message(call.message.chat.id, "🗑 **যে অ্যাডমিনকে রিমুভ করতে চান তার User ID লিখুন:**")

    elif action == "adm_broadcast":
        user_states[user_id] = {"admin_action": "broadcast"}
        bot.send_message(call.message.chat.id, "📢 **সব ইউজারের কাছে যে বার্তাটি পাঠাতে চান তা লিখুন:**")

    elif action == "adm_change_price":
        services = get_services()
        kb = types.InlineKeyboardMarkup(row_width=1)
        for s_name in services:
            kb.add(types.InlineKeyboardButton(s_name, callback_data=f"setp_{services[s_name]['key']}"))
        bot.send_message(call.message.chat.id, "🏷 **যে সার্ভিসের দাম পরিবর্তন করতে চান সিলেক্ট করুন:**", reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data.startswith("setp_"))
def service_price_select(call):
    user_id = call.from_user.id
    if not is_admin(user_id): return
    service_key = call.data.replace("setp_", "")
    user_states[user_id] = {"admin_action": "set_price_value", "service_key": service_key}
    bot.send_message(call.message.chat.id, f"🔢 **প্রতি ১০০০ টি সার্ভিসের জন্য নতুন দাম (TK) লিখুন:**")

# --- Message Processing ---
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    text = message.text
    chat_id = message.chat.id
    user_id = message.from_user.id
    user = get_user(user_id, message.from_user.username, message.from_user.first_name)
    services = get_services()

    # Admin Action Processor
    if user_id in user_states and "admin_action" in user_states[user_id]:
        action = user_states[user_id]["admin_action"]

        if action == "add_balance":
            try:
                target_id, amount = text.split()
                target_id, amount = int(target_id), float(amount)
                conn = sqlite3.connect('smm_panel.db')
                cursor = conn.cursor()
                cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, target_id))
                conn.commit()
                conn.close()
                bot.send_message(chat_id, f"✅ User `{target_id}` এর অ্যাকাউন্টে {amount:.2f} TK জমা হয়েছে।", parse_mode="Markdown")
                bot.send_message(target_id, f"🎉 **অ্যাডমিন আপনার অ্যাকাউন্টে {amount:.2f} টাকা যুক্ত করেছেন!**", parse_mode="Markdown")
            except:
                bot.send_message(chat_id, "❌ ফরম্যাট ভুল হয়েছে! সঠিক ফরম্যাট: `User_ID Amount`", parse_mode="Markdown")
            user_states.pop(user_id, None)
            return

        elif action == "change_support":
            supp_username = text.replace("@", "").strip()
            set_setting("support_contact", supp_username)
            bot.send_message(chat_id, f"✅ নতুন সাপোর্ট অ্যাকাউন্ট সেট করা হয়েছে: @{supp_username}")
            user_states.pop(user_id, None)
            return

        elif action == "add_admin":
            if text.isdigit():
                new_adm = int(text)
                conn = sqlite3.connect('smm_panel.db')
                cursor = conn.cursor()
                cursor.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (new_adm,))
                conn.commit()
                conn.close()
                bot.send_message(chat_id, f"✅ নতুন অ্যাডমিন যুক্ত করা হয়েছে: `{new_adm}`", parse_mode="Markdown")
            else:
                bot.send_message(chat_id, "❌ অকার্যকর ID!")
            user_states.pop(user_id, None)
            return

        elif action == "remove_admin":
            if text.isdigit():
                rem_adm = int(text)
                if rem_adm == SUPER_ADMIN_ID:
                    bot.send_message(chat_id, "❌ সুপার অ্যাডমিনকে রিমুভ করা সম্ভব নয়!")
                else:
                    conn = sqlite3.connect('smm_panel.db')
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM admins WHERE user_id = ?', (rem_adm,))
                    conn.commit()
                    conn.close()
                    bot.send_message(chat_id, f"✅ অ্যাডমিন রিমুভ করা হয়েছে: `{rem_adm}`", parse_mode="Markdown")
            user_states.pop(user_id, None)
            return

        elif action == "set_price_value":
            try:
                new_rate_1k = float(text)
                per_unit_rate = new_rate_1k / 1000.0
                s_key = user_states[user_id]["service_key"]
                conn = sqlite3.connect('smm_panel.db')
                cursor = conn.cursor()
                cursor.execute('UPDATE services SET rate = ? WHERE service_key = ?', (per_unit_rate, s_key))
                conn.commit()
                conn.close()
                bot.send_message(chat_id, f"✅ সার্ভিস এর দাম সফলভাবে পরিবর্তন হয়েছে! নতুন দাম: {new_rate_1k} TK / 1000")
            except:
                bot.send_message(chat_id, "❌ অকার্যকর পরিমাণ! শুধু সংখ্যা লিখুন।")
            user_states.pop(user_id, None)
            return

        elif action == "broadcast":
            conn = sqlite3.connect('smm_panel.db')
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM users')
            users = cursor.fetchall()
            conn.close()
            sent_count = 0
            for u in users:
                try:
                    bot.send_message(u[0], f"📢 **অফিসিয়াল নোটিশ**\n\n{text}", parse_mode="Markdown")
                    sent_count += 1
                except:
                    pass
            bot.send_message(chat_id, f"✅ মোট {sent_count} জন ইউজারের কাছে নোটিফিকেশন পাঠানো হয়েছে।")
            user_states.pop(user_id, None)
            return

    # User Regular Navigation
    if text == "⚙️ Admin Control Panel" and is_admin(user_id):
        bot.send_message(chat_id, "🛠 **WELCOME TO ADMIN PANEL**\n\nনিচের বাটনগুলো দিয়ে পুরো বট নিয়ন্ত্রণ করুন:", reply_markup=admin_panel_keyboard())

    elif text == "🟢 Buy Service":
        bot.send_message(chat_id, "🛒 **সার্ভিস মেনু ওপেন হয়েছে**\n\nনিচের কিবোর্ড থেকে প্ল্যাটফর্ম সিলেক্ট করুন:", reply_markup=platforms_menu())

    elif text in ["🎵 TikTok", "🔵 Facebook", "📷 Instagram", "🎥 YouTube"]:
        bot.send_message(chat_id, f"👉 **{text} এর সার্ভিসসমূহ:**\n\nআপনার কাঙ্খিত সার্ভিসটি বেছে নিন:", reply_markup=sub_services_menu(text))

    elif text in services:
        service_data = services[text]
        user_states[user_id] = {"service_name": text, "step": "quantity", "rate": service_data["rate"], "min": service_data["min"]}
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
        price_msg = "💬 **OFFICIAL SMM SERVICE PRICING** 💬\n━━━━━━━━━━━━━━━━━━━━\n"
        for s_name, data in services.items():
            price_msg += f"🔹 {s_name} = {data['rate']*1000:.2f} TK / 1k\n"
        price_msg += "━━━━━━━━━━━━━━━━━━━━\n🎁 সর্বনিম্ন অর্ডারে সুবিধা প্রযোজ্য।"
        bot.send_message(chat_id, price_msg, parse_mode="Markdown")

    elif text == "💰 Deposit":
        supp = get_setting("support_contact")
        bot.send_message(chat_id, f"💰 **ডিপোজিট সিস্টেম**\n\nআপনার ID: `{user_id}`\n\nটাকা ডিপোজিট করতে অ্যাডমিনকে মেসেজ দিন:\n🔗 **অ্যাডমিন আইডি:** @{supp}", parse_mode="Markdown")

    elif text == "📞 Support":
        supp = get_setting("support_contact")
        inline_sup = types.InlineKeyboardMarkup()
        inline_sup.add(types.InlineKeyboardButton("💬 অ্যাডমিনের সাথে কথা বলুন", url=f"https://t.me/{supp}"))
        bot.send_message(chat_id, "📞 **সাপোর্ট সেন্টার**\nযেকোনো প্রয়োজনে সরাসরি অ্যাডমিনকে মেসেজ দিন।", reply_markup=inline_sup)

    elif text in ["🔙 মেইন মেনু", "🔙 ব্যাক করুন"]:
        bot.send_message(chat_id, "🏠 **মেইন মেনু**", reply_markup=main_menu(user_id))

    # Order Steps
    elif user_id in user_states and "step" in user_states[user_id]:
        state = user_states[user_id]
        if state["step"] == "quantity":
            if not text.isdigit():
                bot.send_message(chat_id, "❌ **দয়া করে শুধু সঠিক সংখ্যা লিখুন!**")
                return
            qty = int(text)
            if qty < state["min"]:
                bot.send_message(chat_id, f"⚠️ **সর্বনিম্ন {state['min']} টি অর্ডার করতে হবে!**")
                return

            cost = qty * state["rate"]
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
            service_name = state["service_name"]

            # Deduct balance & add order to Database
            conn = sqlite3.connect('smm_panel.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET balance = balance - ?, spent = spent + ?, total_orders = total_orders + 1 WHERE user_id = ?',
                           (cost, cost, user_id))
            
            # Fetch all admins to notify them
            cursor.execute('SELECT user_id FROM admins')
            admin_rows = cursor.fetchall()
            conn.commit()
            conn.close()

            # Confirm User
            bot.send_message(chat_id, f"✅ **আপনার অর্ডার সফলভাবে সাবমিট হয়েছে!**\n\n📦 **সার্ভিস:** {service_name}\n🔢 **পরিমাণ:** {qty}\n💰 **কাটা ব্যালেন্স:** {cost:.2f} TK\n🔗 **লিংক:** {link}", reply_markup=main_menu(user_id))

            # Send Notification to ALL Admins
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
            for adm in admin_rows:
                try:
                    bot.send_message(adm[0], admin_notice, parse_mode="Markdown")
                except:
                    pass

            user_states.pop(user_id, None)

if __name__ == '__main__':
    keep_alive()
    print("Bot starting...")
    bot.infinity_polling()
