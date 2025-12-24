import telebot
from telebot import types
from io import BytesIO
import re
import os

# YOUR BOT TOKEN
API_TOKEN = '8493753474:AAGifjXjyimF4GkxjfaIuGTVX9a0mkHXsS0'
bot = telebot.TeleBot(API_TOKEN)

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
        "<b>📥 PLEASE SEND THE PREFIX YOU WANT TO FILTER 🔥</b>\n"
        "<i>(Example: 01785, 01965)</i>"
    )
    bot.reply_to(message, welcome_text, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "reset_prefix")
def reset_prefix_callback(call):
    user_id = call.from_user.id
    user_prefixes.pop(user_id, None)
    bot.answer_callback_query(call.id, "CLEARED")
    bot.send_message(call.message.chat.id, "<b>🔄 SETTINGS RESET. PLEASE SEND A NEW PREFIX.</b>", parse_mode="HTML")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if message.text.startswith('/'):
        return

    user_id = message.from_user.id
    text = message.text.strip()

    # STEP 1: SETTING THE PREFIX
    # এখানে আমরা প্রিফিক্স থেকে + সরিয়ে নিচ্ছি যাতে সার্চ করতে সুবিধা হয়
    if user_id not in user_prefixes or len(text) < 7:
        prefix = text.replace('+', '').replace(' ', '')
        user_prefixes[user_id] = prefix
        bot.reply_to(message, f"<b>🎯 PREFIX SET TO: {prefix}</b>\n\n<b>📥 NOW PASTE YOUR NUMBER LIST.</b>", parse_mode="HTML")
        return

    # STEP 2: PROCESSING THE LIST
    target_prefix = user_prefixes.get(user_id)
    lines = text.split('\n')

    processed_list = []
    for num in lines:
        clean_num = num.strip()
        # এখানে নম্বরটির ভেতর থেকে + সরিয়ে চেক করছি প্রিফিক্সের সাথে মিলে কি না
        search_num = clean_num.replace('+', '') 
        
        if search_num.startswith(target_prefix):
            # আউটপুটে সব সময় + সহ দেখাবে
            if not clean_num.startswith('+'):
                processed_list.append("+" + clean_num)
            else:
                processed_list.append(clean_num)

    # ইউনিক নম্বর রাখা এবং সর্ট করা
    processed = sorted(list(set(processed_list)))

    if processed:
        result_data = "\n".join(processed)
        bio = BytesIO(result_data.encode('utf-8'))
        bio.name = f"Filtered_{target_prefix}.txt"
        bot.send_document(message.chat.id, bio, caption=f"<b>✅ DONE! FOUND {len(processed)} UNIQUE NUMBERS.</b>", parse_mode="HTML", reply_markup=get_reset_markup())
    else:
        bot.reply_to(message, f"<b>❌ NO NUMBERS STARTING WITH {target_prefix} WERE FOUND.</b>", parse_mode="HTML", reply_markup=get_reset_markup())

if __name__ == "__main__":
    print("--- SYSTEM STARTING ---")
    try:
        bot_info = bot.get_me()
        print(f"--- SUCCESS: @{bot_info.username} IS ONLINE ---")
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"--- FAILED TO START: {e} ---")
