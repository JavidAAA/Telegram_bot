import os
import argparse
import json
import time
import asyncio
from dotenv import load_dotenv
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from sdk import bot_response
from eden.client import EdenClient
from eden.client import EdenApiUrls

long_running_tools = [
    "txt2vid",
    "style_mixing",
    "img2vid",
    "vid2vid",
    "video_upscale",
    "vid2vid_sdxl",
    "lora_trainer",
    "animate_3D",
    "reel",
    "story",
]

video_tools = [
    "animate_3D",
    "txt2vid",
    "img2vid",
    "vid2vid_sdxl",
    "style_mixing",
    "video_upscaler",
    "reel",
    "story",
    "lora_trainer",
]

hour_timestamps = {}
day_timestamps = {}

HOUR_IMAGE_LIMIT = 50
HOUR_VIDEO_LIMIT = 10
DAY_IMAGE_LIMIT = 200
DAY_VIDEO_LIMIT = 40

def user_over_rate_limits(user_id):
    if user_id not in hour_timestamps:
        hour_timestamps[user_id] = []
    if user_id not in day_timestamps:
        day_timestamps[user_id] = []

    hour_timestamps[user_id] = [
        t for t in hour_timestamps[user_id] if time.time() - t["time"] < 3600
    ]
    day_timestamps[user_id] = [
        t for t in day_timestamps[user_id] if time.time() - t["time"] < 86400
    ]

    hour_video_tool_calls = len(
        [t for t in hour_timestamps[user_id] if t["tool"] in video_tools]
    )
    hour_image_tool_calls = len(
        [t for t in hour_timestamps[user_id] if t["tool"] not in video_tools]
    )

    day_video_tool_calls = len(
        [t for t in day_timestamps[user_id] if t["tool"] in video_tools]
    )
    day_image_tool_calls = len(
        [t for t in day_timestamps[user_id] if t["tool"] not in video_tools]
    )

    # print("hour_video_tool_calls", hour_video_tool_calls)
    # print("hour_image_tool_calls", hour_image_tool_calls)
    # print("day_video_tool_calls", day_video_tool_calls)
    # print("day_image_tool_calls", day_image_tool_calls)

    if (
        hour_video_tool_calls >= HOUR_VIDEO_LIMIT
        or hour_image_tool_calls >= HOUR_IMAGE_LIMIT
    ):
        return True
    if (
        day_video_tool_calls >= DAY_VIDEO_LIMIT
        or day_image_tool_calls >= DAY_IMAGE_LIMIT
    ):
        return True
    return False

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def start(
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
    update.message.reply_text('Hello! I am your asynchronous bot.')

async def echo(
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
    chat_id, chat_type, is_direct_message, is_bot_mentioned_or_replied = await handler_mention_type(update, context)
    user_id, user_name, first_name, last_name, full_name = get_user_info(update) 
    if update.message.photo:
        content = "photo"
    elif update.message.text:
        content = update.message.text
    else:
        content = "unsupported content type"
    chat_message = {
        "name": f"User_{user_id}",
        "content": content,
        "attachments": [],
        "settings": {}
    }
    media_url = bot_response(content)
    
    if is_direct_message:
        await context.bot.send_photo(chat_id=chat_id, photo=media_url)
    elif is_bot_mentioned_or_replied:
        await context.bot.send_photo(chat_id=chat_id, photo=media_url)
    else:
        return

def error_handler(
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
    logging.error("Exception while handling an update:", exc_info=context.error)

async def handler_mention_type(
        update : Update , 
        context : ContextTypes.DEFAULT_TYPE
    ) -> tuple[int, str, bool, bool]:
    message = update.message
    chat_id = message.chat.id
    chat_type = message.chat.type
    is_direct_message = chat_type == 'private'
    
    bot_username = (await context.bot.get_me()).username

    is_bot_mentioned = False
    if message.entities:
        for entity in message.entities:
            if entity.type == 'mention' and message.text[entity.offset:entity.offset + entity.length].lower() == f"@{bot_username.lower()}":
                is_bot_mentioned = True
                break

    is_replied_to_bot = message.reply_to_message and message.reply_to_message.from_user.username == bot_username

    is_bot_mentioned_or_replied = is_bot_mentioned or is_replied_to_bot
    
    return chat_id, chat_type, is_direct_message, is_bot_mentioned_or_replied

def get_user_info(update:Update) -> tuple[int, str, str, str, str]:
    message = update.message
    user_id = message.from_user.id
    user_name = message.from_user.username

    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""
    full_name = f"{first_name} {last_name}".strip()

    return user_id, user_name, first_name, last_name, full_name

def main(
    env:str,
) -> None:
    load_dotenv(env)
    BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.add_error_handler(error_handler)

    application.run_polling()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="MarsBot")
    parser.add_argument("--env", help="Path to the .env file to load", default=".env")
    args = parser.parse_args()
    main(args.env)