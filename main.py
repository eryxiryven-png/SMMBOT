import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread

# Bot Token & Admin Setup
API_TOKEN = "8761302883:AAGGgeUVSjQkuucXQXdJHtPHz-Gw2HQ9dT8"
ADMIN_ID = 8764166382

bot = telebot.TeleBot(API_TOKEN)

# Dummy Web Server for Render 24/7 Hosting
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Alive & Running 24/7!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- Keyboards ---
def main_menu():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        KeyboardButton("🟢 Buy Service"),
        KeyboardButton("💰 Deposit"),
        KeyboardButton("📜 Service Price"),
        KeyboardButton("👤 My Profile"),
        KeyboardButton("📞 Support")
    )
    return markup

def services_menu():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        KeyboardButton("🎵 TikTok"),
        KeyboardButton("🔵 Facebook"),
        KeyboardButton("📷 Instagram"),
        KeyboardButton("✈️ Telegram"),
        KeyboardButton("🎥 YouTube"),
        KeyboardButton("🐤 Twitter"),
        KeyboardButton("🔙 মেইন মেনু")
    )
    return markup

# --- Handlers ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Channel Force Join Buttons
    inline_kb = InlineKeyboardMarkup()
    inline_kb.add(InlineKeyboardButton("🚀 Join Channel", url="https://t.me/JUSTTRUSTBR0"))
    inline_kb.add(InlineKeyboardButton("👥 Join Group", url="https://t.me/buyselgroup0"))
    inline_kb.add(InlineKeyboardButton("⚡ Verify Membership", callback_data="verify"))

    welcome_text = (
        "👑 **WELCOME TO SERVICE MASTER** ⚡\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "বটটি ব্যবহার করতে নিচের চ্যানেল ও গ্রুপে অবশ্যই জয়েন করুন।\n"
        "জয়েন না করলে অ্যাকাউন্ট ভেরিফাই হবে না।\n\n"
        "📢 অফিসিয়াল চ্যানেল: @JUSTTRUSTBR0\n"
        "💬 অফিসিয়াল গ্রুপ: @buyselgroup0\n\n"
        "🟢 জয়েন শেষ হলে নিচে Verify বাটনে ক্লিক করুন!"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=inline_kb)

@bot.callback_query_handler(func=lambda call: call.data == "verify")
def verify_callback(call):
    bot.answer_callback_query(call.id, "✅ Account Verified Successfully!")
    dash_text = (
        "🌟 **SERVICE MASTER DASHBOARD** 🌟\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **ইউজার:** {call.from_user.first_name}\n"
        "💰 **ব্যালেন্স:** 0.00 TK\n"
        "📊 **মোট খরচ:** 0.00 TK\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "নিচের বাটন থেকে সার্ভিস অর্ডার করুন:"
    )
    bot.send_message(call.message.chat.id, dash_text, parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text

    if text == "🟢 Buy Service":
        bot.send_message(message.chat.id, "🛒 **সার্ভিস মেনু ওপেন হয়েছে**\n\nনিচের কিবোর্ড থেকে আপনার পছন্দের সোশ্যাল মিডিয়া সিলেক্ট করুন:", reply_markup=services_menu())

    elif text == "📜 Service Price":
        price_list = (
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
            "🎁 **বিশেষ দ্রষ্টব্য:** সর্বনিম্ন ১ টাকা অর্ডার করতে পারবেন।"
        )
        bot.send_message(message.chat.id, price_list, parse_mode="Markdown")

    elif text == "💰 Deposit":
        bot.send_message(message.chat.id, "💰 **আপনি কত টাকা ডিপোজিট করতে চান?**\n⚠️ সর্বনিম্ন ১০ টাকা এবং সর্বোচ্চ ৫০০০ টাকা।\n\nএডমিন আইডি: @justtrustbro")

    elif text == "👤 My Profile":
        profile_text = (
            "👤 **USER ACCOUNT DETAILS** 👤\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"📛 **নাম:** {message.from_user.first_name}\n"
            f"🆔 **আইডি:** `{message.from_user.id}`\n"
            f"🔗 **ইউজার:** @{message.from_user.username}\n\n"
            "💰 **ব্যালেন্স:** 0.00 TK\n"
            "💸 **খরচ করেছেন:** 0.00 TK\n\n"
            "📊 **স্ট্যাটাস:** Verified ✅"
        )
        bot.send_message(message.chat.id, profile_text, parse_mode="Markdown")

    elif text == "📞 Support":
        inline_sup = InlineKeyboardMarkup()
        inline_sup.add(InlineKeyboardButton("💬 অ্যাডমিনের সাথে কথা বলুন", url="https://t.me/justtrustbro"))
        bot.send_message(
            message.chat.id,
            "📞 **সাপোর্ট সেন্টার (Support Center)**\n\n"
            "আমাদের সার্ভিস নিয়ে কোনো সমস্যা হলে বা কিছু জানার থাকলে সরাসরি অ্যাডমিনের সাথে যোগাযোগ করুন।\n\n"
            "⏰ **সাপোর্ট সময়:** সকাল ১০টা - রাত ১০টা",
            reply_markup=inline_sup
        )

    elif text == "🔙 মেইন মেনু":
        bot.send_message(message.chat.id, "🏠 **মেইন মেনু**", reply_markup=main_menu())

if __name__ == '__main__':
    keep_alive()  # Runs HTTP server for 24/7 uptime
    print("Bot starting...")
    bot.infinity_polling()
