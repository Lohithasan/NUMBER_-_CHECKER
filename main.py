import telebot
from telebot import types
from io import BytesIO
import re
import os

# YOUR BOT TOKEN
API_TOKEN = '8493753474:AAGifjXjyimF4GkxjfaIuGTVX9a0mkHXsS0'
bot = telebot.TeleBot(API_TOKEN)

# DICTIONARY TO STORE THE PREFIX LIST
user_prefixes = {}

def get_reset_markup():
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("🔄 START OVER", callback_data="reset_prefix")
    markup.add(btn)
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_id = message.from_user.id
    user_prefixes.pop(user_id, None)

    welcome_text = (
        "<b>🎉 Welcome To BUBALULA BOT 🤖✨</b>\n\n"
        "<b>💥 Bot Created By @Lohit_69💎</b>\n\n"
        "<b>📥 PLEASE SEND THE PREFIX(ES) YOU WANT TO FILTER 🔥</b>\n"
        "<i>(Example: 01785, 01965 or 0177 0178 0179)</i>"
    )
    bot.reply_to(message, welcome_text, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "reset_prefix")
def reset_prefix_callback(call):
    user_id = call.from_user.id
    user_prefixes.pop(user_id, None)
    bot.answer_callback_query(call.id, "CLEARED")
    bot.send_message(
        call.message.chat.id,
        "<b>🔄 SETTINGS RESET. PLEASE SEND NEW PREFIX(ES).</b>",
        parse_mode="HTML"
    )

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if message.text.startswith('/'):
        return

    user_id = message.from_user.id
    text = message.text.strip()

    # STEP 1: SETTING THE PREFIXES (Check if input looks like prefixes)
    # যদি ইনপুট ছোট হয় অথবা ইউজারের আগে থেকে কোনো প্রিফিক্স সেভ না থাকে
    if user_id not in user_prefixes or len(text) < 15: # ১৬-২০ ডিজিটের বেশি হলে সেটা লিস্ট হিসেবে গণ্য হবে
        # স্পেস বা কমা দিয়ে আলাদা করে প্রিফিক্সগুলো লিস্টে নিচ্ছি
        raw_prefixes = re.split(r'[ ,]+', text)
        # প্রিফিক্স থেকে + চিহ্ন এবং বাড়তি স্পেস সরিয়ে ক্লিন করছি
        clean_prefixes = [p.replace('+', '').strip() for p in raw_prefixes if p.strip()]
        
        if clean_prefixes:
            user_prefixes[user_id] = clean_prefixes
            display_prefixes = ", ".join(clean_prefixes)
            bot.reply_to(
                message, 
                f"<b>🎯 PREFIXES SET TO: {display_prefixes}</b>\n\n"
                f"<b>📥 NOW PASTE YOUR NUMBER LIST.</b>",
                parse_mode="HTML"
            )
            return

    # STEP 2: PROCESSING THE LIST
    target_prefixes = user_prefixes.get(user_id, [])
    lines = text.split('\n')

    processed_list = []
    for num in lines:
        clean_num = num.strip()
        # নম্বর থেকে + সরিয়ে চেক করছি
        search_num = clean_num.replace('+', '')
        
        # চেক করছি নম্বরটি সেভ করা প্রিফিক্সগুলোর কোনো একটির সাথে মিলে কি না
        match = False
        for pref in target_prefixes:
            if search_num.startswith(pref):
                match = True
                break
        
        if match:
            # আউটপুটে + ফরম্যাট ঠিক করা
            if not clean_num.startswith('+'):
                processed_list.append("+" + clean_num)
            else:
                processed_list.append(clean_num)

    # ইউনিক নম্বর এবং সর্টিং
    processed = sorted(list(set(processed_list)))

    if processed:
        result_data = "\n".join(processed)
        bio = BytesIO(result_data.encode('utf-8'))
        bio.name = "Filtered_Numbers.txt"

        bot.send_document(
            message.chat.id,
            bio,
            caption=f"<b>✅ DONE! FOUND {len(processed)} UNIQUE NUMBERS FOR YOUR PREFIXES.</b>",
            parse_mode="HTML",
            reply_markup=get_reset_markup()
        )
    else:
        bot.reply_to(
            message,
            f"<b>❌ NO NUMBERS STARTING WITH THE GIVEN PREFIXES WERE FOUND.</b>",
            parse_mode="HTML",
            reply_markup=get_reset_markup()
        )

# --- STARTUP ---
if __name__ == "__main__":
    print("--- SYSTEM STARTING ---")
    try:
        bot_info = bot.get_me()
        print(f"--- SUCCESS: @{bot_info.username} IS ONLINE ---")
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"--- FAILED TO START: {e} ---")
