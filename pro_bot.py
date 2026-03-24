import sys
import types

module = types.ModuleType("imghdr")
sys.modules["imghdr"] = module
import logging
import json
import os
import uuid
import time
import threading

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

logging.basicConfig(level=logging.INFO)

TOKEN = "8611933616:AAHyXO8O02TirpLauAKdCViCx37y_bTlNXQ"
CHANNEL_USERNAME = "animezone1896"

DB_FILE = "videos.json"

if os.path.exists(DB_FILE):
    try:
        with open(DB_FILE, "r") as f:
            video_db = json.load(f)
    except:
        video_db = {}
else:
    video_db = {}

user_limit = {}
DAILY_LIMIT = 5

def save_db():
    with open(DB_FILE, "w") as f:
        json.dump(video_db, f)

def start(update: Update, context: CallbackContext):
    try:
        args = context.args

        if args:
            key = args[0]

            if key in video_db:
                video = video_db[key]

                keyboard = [
                    [InlineKeyboardButton("Join Channel", url="https://t.me/animezone1896")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                msg = update.message.reply_video(
                    video=video,
                    caption="🔥 Watch Now\n⏱ Delete in 1 hour",
                    reply_markup=reply_markup
                )

                threading.Timer(3600, delete_msg, args=(context, msg.chat_id, msg.message_id)).start()
            else:
                update.message.reply_text("Invalid link.")
        else:
            update.message.reply_text("Send video to get link.")

    except Exception as e:
        update.message.reply_text("Error occurred")

def handle_video(update: Update, context: CallbackContext):
    try:
        user_id = update.message.from_user.id
        today = time.strftime("%Y-%m-%d")

        if user_id not in user_limit:
            user_limit[user_id] = {"date": today, "count": 0}

        if user_limit[user_id]["date"] != today:
            user_limit[user_id] = {"date": today, "count": 0}

        if user_limit[user_id]["count"] >= DAILY_LIMIT:
            update.message.reply_text("Daily limit reached (5).")
            return

        user_limit[user_id]["count"] += 1

        video_id = update.message.video.file_id
        key = str(uuid.uuid4())[:8]

        video_db[key] = video_id
        save_db()

        link = f"https://t.me/Animezone189_bot?start={key}"

        update.message.reply_text(f"Your Link:\n{link}")

    except Exception as e:
        update.message.reply_text("Error sending link")

def delete_msg(context, chat_id, message_id):
    try:
        context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except:
        pass

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.video, handle_video))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
