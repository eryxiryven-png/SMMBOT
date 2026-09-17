import sqlite3
import telebot
from telebot import types
from flask import Flask
from threading import Thread

API_TOKEN = "8761302883:AAGGgeUVSjQkuucXQXdJHtPHz-Gw2HQ9dT8"
SUPER_ADMIN_ID = 8764166382  # আপনার আইডি

ORDER_LOG_CHANNEL = "@SMMproLiat" 

bot = telebot.TeleBot(API_TOKEN)

# --- Database Management ---
def init_db():
    conn = sqlite3.connect('smm_panel.db')
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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            service_key TEXT PRIMARY KEY,
            service_name TEXT,
            rate REAL,
            min_qty INTEGER
        )
    ''')
    
    cursor.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (SUPER_ADMIN_ID,))
    cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES ("support_contact", "EREN_Zz")')
    cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES ("bkash_no", "01700000000")')
    cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES ("nagad_no", "01700000000")')
    cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES ("rocket_no", "01700000000")')
    cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES ("gateway_link", "https://yourpaymentgateway.com")')
    cursor.execute('REPLACE INTO settings (key, value) VALUES ("log_channel", ?)', (ORDER_LOG_CHANNEL,))

    # আপনার দেয়া সর্বশেষ প্রাইস লিস্ট (১০০০ টির রেট অনুযায়ী পার ইউনিট বের করে সেট করা হয়েছে)
    default_services = [
        # Telegram
        ("tg_member_norefill", "💥 TG 1K Member (NoRefill)", 0.03, 34),
        ("tg_member_lifetime", "💥 TG 1K Lifetime Member", 0.16, 7),
        ("tg_post_view", "💥 TG Post View 1K", 0.003, 334),
        ("tg_post_react", "💥 TG Post React 1K", 0.01, 100),
        ("tg_vote", "💥 TG 100 Vote", 0.30, 4),
        
        # TikTok
        ("tiktok_like", "💥 TikTok 1K Like", 0.04, 25),
        ("tiktok_views", "💥 TikTok 10K View", 0.003, 334),
        ("tiktok_followers", "💥 TikTok 1K Follower", 0.20, 5),
        ("tiktok_share", "💥 TikTok 1K Share", 0.02, 50),
        ("tiktok_comment", "💥 TikTok 100 Real Comment", 0.40, 3),

        # YouTube
        ("yt_subscribe", "💥 YT 1K Subscriber", 0.19, 6),
        ("yt_like", "💥 YT 1K Like", 0.05, 20),
        ("yt_views", "💥 YT 1K View", 0.13, 8),
        ("yt_comment", "💥 YT 100 Comment", 0.40, 3),

        # Instagram
        ("ig_followers", "💥 IG 1K Follower", 0.15, 7),
        ("ig_views_10k", "💥 IG 10K View", 0.001, 1000),
        ("ig_views_100k", "💥 IG 100K View", 0.0007, 1429),
        ("ig_like", "💥 IG 1K Like", 0.04, 25),

        # Facebook
        ("fb_real_follower", "💥 FB 1K Real Follower", 0.06, 17),
        ("fb_post_react", "💥 FB 1K Post React", 0.075, 14),
        ("fb_comment", "💥 FB 100 Real Comment", 0.40, 3),
        ("fb_share", "💥 FB 1K Share", 0.10, 10),
        ("fb_video_views", "💥 FB 1K Video View", 0.02, 50)
    ]
    
    for s_key, s_name, rate, min_q in default_services:
        cursor.execute('REPLACE INTO services (service_key, service_name, rate, min_qty) VALUES (?, ?, ?, ?)',
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
    markup.add("💥 টেলিগ্রাম", "💥 টিকটক", "💥 ইউটিউব", "💥 ইন্সট্রাগ্রাম", "💥 ফেসবুক", "🔙 মেইন মেনু")
    return markup

def sub_services_menu(platform):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    if platform == "💥 টেলিগ্রাম":
        markup.add("💥 TG 1K Member (NoRefill)", "💥 TG 1K Lifetime Member", "💥 TG Post View 1K", "💥 TG Post React 1K", "💥 TG 100 Vote")
    elif platform == "💥 টিকটক":
        markup.add("💥 TikTok 1K Like", "💥 TikTok 10K View", "💥 TikTok 1K Follower", "💥 TikTok 1K Share", "💥 TikTok 100 Real Comment")
    elif platform == "💥 ইউটিউব":
        markup.add("💥 YT 1K Subscriber", "💥 YT 1K Like", "💥 YT 1K View", "💥 YT 100 Comment")
    elif platform == "💥 ইন্সট্রাগ্রাম":
        markup.add("💥 IG 1K Follower", "💥 IG 10K View", "💥 IG 100K View", "💥 IG 1K Like")
    elif platform == "💥 ফেসবুক":
        markup.add("💥 FB 1K Real Follower", "💥 FB 1K Post React", "💥 FB 100 Real Comment", "💥 FB 1K Share", "💥 FB 1K Video View")
    markup.add("🔙 ব্যাক করুন")
    return markup

def admin_panel_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💳 Add Balance", callback_data="adm_add_bal"),
        types.InlineKeyboardButton("⚙️ Deposit Settings", callback_data="adm_dep_settings"),
        types.InlineKeyboardButton("🏷 Change Price", callback_data="adm_change_price"),
        types.InlineKeyboardButton("📞 Change Support ID", callback_data="adm_change_supp"),
        types.InlineKeyboardButton("📢 Change Log Channel", callback_data="adm_change_log"),
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
    inline_kb.add(types.InlineKeyboardButton("🚀 Join Channel", url="https://t.me/SMMproLiat"))
    inline_kb.add(types.InlineKeyboardButton("⚡ Verify Membership", callback_data="verify"))

    welcome_text = (
        "👑 **WELCOME TO SMM PRO** ⚡\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "বটটি ব্যবহার করতে নিচের চ্যানেলে জয়েন করুন।\n"
        "📢 অফিসিয়াল চ্যানেল: @SMMproLiat\n\n"
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

# --- Admin Callbacks ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_"))
def admin_callbacks(call):
    user_id = call.from_user.id
    if not is_admin(user_id):
        bot.answer_callback_query(call.id, "❌ আপনি অ্যাডমিন নন!", show_alert=True)
        return

    action = call.data

    if action == "adm_add_bal":
        user_states[user_id] = {"admin_action": "add_balance"}
        bot.send_message(call.message.chat.id, "💳 **ব্যালেন্স অ্যাড ফরম্যাট:**\n`User_ID Amount`\n\nউদাহরণ: `6587881288 100`", parse_mode="Markdown")

    elif action == "adm_dep_settings":
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(
            types.InlineKeyboardButton("📱 bKash Number", callback_data="set_bkash"),
            types.InlineKeyboardButton("📱 Nagad Number", callback_data="set_nagad"),
            types.InlineKeyboardButton("📱 Rocket Number", callback_data="set_rocket"),
            types.InlineKeyboardButton("🌐 Gateway Link", callback_data="set_gateway")
        )
        bot.send_message(call.message.chat.id, "⚙️ **ডিপোজিট সিস্টেম সেটআপ:**", reply_markup=kb)

    elif action == "adm_change_supp":
        user_states[user_id] = {"admin_action": "change_support"}
        bot.send_message(call.message.chat.id, "📞 **নতুন সাপোর্ট ইউজারনেমটি লিখুন (@ ছাড়া):**")

    elif action == "adm_change_log":
        user_states[user_id] = {"admin_action": "change_log_channel"}
        bot.send_message(call.message.chat.id, "📢 **অর্ডার লগ চ্যানেল Username বা ID দিন:**\nউদাহরণ: `@SMMproLiat`")

    elif action == "adm_add_admin":
        user_states[user_id] = {"admin_action": "add_admin"}
        bot.send_message(call.message.chat.id, "👥 **নতুন অ্যাডমিনের Telegram User ID লিখুন:**")

    elif action == "adm_rem_admin":
        user_states[user_id] = {"admin_action": "remove_admin"}
        bot.send_message(call.message.chat.id, "🗑 **অ্যাডমিনের User ID লিখুন:**")

    elif action == "adm_broadcast":
        user_states[user_id] = {"admin_action": "broadcast"}
        bot.send_message(call.message.chat.id, "📢 **ব্রডকাস্ট করার মেসেজটি লিখুন:**")

    elif action == "adm_change_price":
        services = get_services()
        kb = types.InlineKeyboardMarkup(row_width=1)
        for s_name in services:
            kb.add(types.InlineKeyboardButton(s_name, callback_data=f"setp_{services[s_name]['key']}"))
        bot.send_message(call.message.chat.id, "🏷 **যে সার্ভিসের দাম পরিবর্তন করতে চান সিলেক্ট করুন:**", reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_"))
def deposit_settings_select(call):
    user_id = call.from_user.id
    if not is_admin(user_id): return
    key = call.data.replace("set_", "")
    user_states[user_id] = {"admin_action": f"set_{key}"}
    bot.send_message(call.message.chat.id, f"📝 **নতুন {key.upper()} তথ্যটি লিখুন:**")

@bot.callback_query_handler(func=lambda call: call.data.startswith("setp_"))
def service_price_select(call):
    user_id = call.from_user.id
    if not is_admin(user_id): return
    service_key = call.data.replace("setp_", "")
    user_states[user_id] = {"admin_action": "set_price_value", "service_key": service_key}
    bot.send_message(call.message.chat.id, "🔢 **নতুন প্রতি ১০০০ টি বা ১ টি সার্ভিসের গড় দাম কত দিতে চান?**")

# --- Deposit Option Handlers ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("dep_"))
def deposit_method_handler(call):
    user_id = call.from_user.id
    method = call.data.replace("dep_", "")
    supp = get_setting("support_contact")
    
    if method == "manual":
        bkash = get_setting("bkash_no")
        nagad = get_setting("nagad_no")
        rocket = get_setting("rocket_no")
        
        msg = (
            "📌 **ম্যানুয়াল ডিপোজিট তথ্য (Personal)**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🔹 **bKash:** `{bkash}`\n"
            f"🔹 **Nagad:** `{nagad}`\n"
            f"🔹 **Rocket:** `{rocket}`\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ **কীভাবে ক্যাশআউট / সেন্ড মানি করবেন:**\n"
            "১. উপরে উল্লেখিত নম্বরে টাকা পাঠান।\n"
            "২. টাকা পাঠানোর পর আপনার **ইউজার আইডি (`" + str(user_id) + "`)**, **কত টাকা পাঠিয়েছেন** এবং **TrxID** অ্যাডমিনকে পাঠান।\n\n"
            f"📞 **অ্যাডমিন আইডিতে মেসেজ দিন:** @{supp}"
        )
        bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")
        
    elif method == "gateway":
        gw_link = get_setting("gateway_link")
        inline_gw = types.InlineKeyboardMarkup()
        inline_gw.add(types.InlineKeyboardButton("💳 Pay Online Now", url=gw_link))
        bot.send_message(call.message.chat.id, "🌐 **ডাইরেক্ট পেমেন্ট গেটওয়ে**\n\nনিচের লিংকে ক্লিক করে বিকাশ/নগদ/রকেট/কার্ড দিয়ে ইনস্ট্যান্ট অটো ডিপোজিট করুন:", reply_markup=inline_gw)

# --- Messages Handling ---
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    text = message.text
    chat_id = message.chat.id
    user_id = message.from_user.id
    user = get_user(user_id, message.from_user.username, message.from_user.first_name)
    services = get_services()

    # Admin Processing
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
                bot.send_message(chat_id, "❌ ফরম্যাট ভুল হয়েছে!")
            user_states.pop(user_id, None)
            return

        elif action in ["set_bkash", "set_nagad", "set_rocket", "set_gateway"]:
            key = action.replace("set_", "") + ("_no" if "gateway" not in action else "_link")
            set_setting(key, text.strip())
            bot.send_message(chat_id, f"✅ {key.upper()} সফলভাবে আপডেট করা হয়েছে!")
            user_states.pop(user_id, None)
            return

        elif action == "change_support":
            supp_username = text.replace("@", "").strip()
            set_setting("support_contact", supp_username)
            bot.send_message(chat_id, f"✅ নতুন সাপোর্ট অ্যাকাউন্ট: @{supp_username}")
            user_states.pop(user_id, None)
            return

        elif action == "change_log_channel":
            log_chan = text.strip()
            set_setting("log_channel", log_chan)
            bot.send_message(chat_id, f"✅ অর্ডার লগ চ্যানেল আপডেট হয়েছে: `{log_chan}`", parse_mode="Markdown")
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
                bot.send_message(chat_id, f"✅ নতুন অ্যাডমিন যুক্ত হয়েছে: `{new_adm}`", parse_mode="Markdown")
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
                bot.send_message(chat_id, f"✅ দাম পরিবর্তন সফল হয়েছে!")
            except:
                bot.send_message(chat_id, "❌ সংখ্যা লিখুন!")
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
            bot.send_message(chat_id, f"✅ মোট {sent_count} জন ইউজারের কাছে পাঠানো হয়েছে।")
            user_states.pop(user_id, None)
            return

    # User Core System
    if text == "⚙️ Admin Control Panel" and is_admin(user_id):
        bot.send_message(chat_id, "🛠 **WELCOME TO ADMIN PANEL**\n\nনিচের বাটনগুলো দিয়ে বট নিয়ন্ত্রণ করুন:", reply_markup=admin_panel_keyboard())

    elif text == "🟢 Buy Service":
        bot.send_message(chat_id, "🛒 **সার্ভিস মেনু ওপেন হয়েছে**\n\nনিচের কিবোর্ড থেকে প্ল্যাটফর্ম সিলেক্ট করুন:", reply_markup=platforms_menu())

    elif text in ["💥 টেলিগ্রাম", "💥 টিকটক", "💥 ইউটিউব", "💥 ইন্সট্রাগ্রাম", "💥 ফেসবুক"]:
        bot.send_message(chat_id, f"👉 **{text} এর সার্ভিসসমূহ:**\n\nআপনার কাঙ্খিত সার্ভিসটি বেছে নিন:", reply_markup=sub_services_menu(text))

    elif text in services:
        service_data = services[text]
        user_states[user_id] = {"service_name": text, "step": "quantity", "rate": service_data["rate"], "min": service_data["min"]}
        
        min_cost = service_data["min"] * service_data["rate"]
        bot.send_message(
            chat_id,
            f"🎯 **{text}**\n"
            f"⚠️ সর্বনিম্ন অর্ডার পরিমাণ: {service_data['min']} টি (সর্বনিম্ন ১ টাকা অর্ডার গ্রহণযোগ্য)\n\n"
            f"🔢 **আপনি কতগুলো নিতে চান? (শুধু সংখ্যা লিখুন):**"
        )

    elif text == "👤 My Profile":
        username_str = f"@{user[1]}" if user[1] else "Not Set"
        profile_text = (
            "👤 **USER ACCOUNT DETAILS** 👤\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"📛 **নাম:** {user[2]}\n"
            f"🆔 **আইডি:** `{user[0]}`\n"
            f"🔗 **ইউজারনেম:** {username_str}\n\n"
            f"💰 **বর্তমান ব্যালেন্স:** {user[3]:.2f} TK\n"
            f"💸 **মোট খরচ:** {user[4]:.2f} TK\n"
            f"📦 **মোট অর্ডার সংখ্যা:** {user[5]} টি\n"
            "📊 **স্ট্যাটাস:** Verified User ✅\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        bot.send_message(chat_id, profile_text, parse_mode="Markdown")

    elif text == "📜 Service Price":
        supp = get_setting("support_contact")
        price_msg = (
            "💬 **SOCIAL MEDIA ALL SERVICE** 💬\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "💥 **টেলিগ্রাম লিস্ট** 👇\n"
            "🔹 1K Member = 30 TK (NoRefill)\n"
            "🔹 1K Lifetime Member = 160 TK\n"
            "🔹 Post View 1K = 3 TK\n"
            "🔹 Post React 1K = 10 TK\n"
            "🔹 100 Vote = 30 TK\n\n"
            "💥 **টিকটক** 👇\n"
            "🔹 1K Like = 40 TK\n"
            "🔹 10K View = 30 TK\n"
            "🔹 1K Follower = 200 TK\n"
            "🔹 1K Share = 20 TK\n"
            "🔹 100 Real Comment = 40 TK\n\n"
            "💥 **ইউটিউব** 👇\n"
            "🔹 1K Subscriber = 190 TK\n"
            "🔹 1K Like = 50 TK\n"
            "🔹 1K View = 130 TK\n"
            "🔹 100 Comment = 40 TK\n\n"
            "💥 **ইন্সট্রাগ্রাম** 👇\n"
            "🔹 1K Follower = 150 TK\n"
            "🔹 10K View = 10 TK\n"
            "🔹 100K View = 70 TK\n"
            "🔹 1K Like = 40 TK\n\n"
            "💥 **ফেসবুক** 👇\n"
            "🔹 1K Real Follower = 60 TK\n"
            "🔹 1K Post React = 75 TK\n"
            "🔹 100 Real Comment = 40 TK\n"
            "🔹 1K Share = 100 TK\n"
            "🔹 1K Video View = 20 TK\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🎁 **বিশেষ দ্রষ্টব্য:** সর্বনিম্ন ১ টাকা অর্ডার করতে পারবেন।\n\n"
            f"📞 **বিস্তারিত জানতে:** @{supp}"
        )
        bot.send_message(chat_id, price_msg, parse_mode="Markdown")

    elif text == "💰 Deposit":
        dep_markup = types.InlineKeyboardMarkup(row_width=2)
        dep_markup.add(
            types.InlineKeyboardButton("📱 bKash / Nagad / Rocket", callback_data="dep_manual"),
            types.InlineKeyboardButton("🌐 Direct Payment Gateway", callback_data="dep_gateway")
        )
        bot.send_message(
            chat_id,
            "💰 **ডিপোজিট সিস্টেম**\n\n"
            "পেমেন্ট মাধ্যম সিলেক্ট করুন:\n"
            "১. **bKash / Nagad / Rocket:** ম্যানুয়ালি টাকা পাঠিয়ে অ্যাডমিন সাপোর্ট থেকে এড করান।\n"
            "২. **Direct Payment Gateway:** পেমেন্ট গেটওয়ে দিয়ে ইনস্ট্যান্ট ডিপোজিট করুন।",
            reply_markup=dep_markup
        )

    elif text == "📞 Support":
        supp = get_setting("support_contact")
        inline_sup = types.InlineKeyboardMarkup()
        inline_sup.add(types.InlineKeyboardButton("💬 অ্যাডমিনের সাথে কথা বলুন", url=f"https://t.me/{supp}"))
        bot.send_message(chat_id, "📞 **সাপোর্ট সেন্টার**\nযেকোনো প্রয়োজনে সরাসরি অ্যাডমিনকে মেসেজ দিন।", reply_markup=inline_sup)

    elif text in ["🔙 মেইন মেনু", "🔙 ব্যাক করুন"]:
        bot.send_message(chat_id, "🏠 **মেইন মেনু**", reply_markup=main_menu(user_id))

    # Order Placement Processing
    elif user_id in user_states and "step" in user_states[user_id]:
        state = user_states[user_id]
        if state["step"] == "quantity":
            if not text.isdigit():
                bot.send_message(chat_id, "❌ **দয়া করে শুধু সঠিক সংখ্যা লিখুন!**")
                return
            qty = int(text)
            cost = qty * state["rate"]
            
            if cost < 1.0:
                bot.send_message(chat_id, f"⚠️ **সর্বনিম্ন ১ টাকার অর্ডার করতে হবে!** (আপনার দেওয়া পরিমাণের খরচ: {cost:.2f} TK)")
                return

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

            # Deduct Balance
            conn = sqlite3.connect('smm_panel.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET balance = balance - ?, spent = spent + ?, total_orders = total_orders + 1 WHERE user_id = ?',
                           (cost, cost, user_id))
            
            cursor.execute('SELECT user_id FROM admins')
            admin_rows = cursor.fetchall()
            conn.commit()
            conn.close()

            # Confirm to User
            bot.send_message(chat_id, f"✅ **আপনার অর্ডার সফলভাবে সাবমিট হয়েছে!**\n\n📦 **সার্ভিস:** {service_name}\n🔢 **পরিমাণ:** {qty}\n💰 **কাটা ব্যালেন্স:** {cost:.2f} TK\n🔗 **লিংক:** {link}", reply_markup=main_menu(user_id))

            # Send Notification to Admins
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

            # Auto Post to Public Log Channel
            log_chan = get_setting("log_channel")
            if log_chan:
                channel_msg = (
                    "🆓 **NEW AUTO ORDER SUCCESS** 🆓\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    f"👤 **ইউজার:** {user[2]}\n"
                    f"📦 **সার্ভিস:** {service_name}\n"
                    f"🔢 **পরিমাণ:** {qty}\n"
                    f"💰 **মোট খরচ:** {cost:.2f} TK\n"
                    "✅ **স্ট্যাটাস:** Processing"
                )
                try:
                    bot.send_message(log_chan, channel_msg, parse_mode="Markdown")
                except Exception as e:
                    print(f"Log Channel Post Error: {e}")

            user_states.pop(user_id, None)

if __name__ == '__main__':
    keep_alive()
    print("Bot starting...")
    bot.infinity_polling()
