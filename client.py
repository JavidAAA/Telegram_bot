# import os
# import argparse
# import json
# import re
# import time
# from dotenv import load_dotenv
# import logging
# from telegram import Update
# from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
# from sdk import bot_response
# from eden.client import EdenClient
# from eden.client import EdenApiUrls




# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )

# def error_handler(
#         update: Update, 
#         context: ContextTypes.DEFAULT_TYPE
#     ) -> None:
#     logging.error("Exception while handling an update:", exc_info=context.error)

# async def handler_mention_type(
#         update : Update , 
#         context : ContextTypes.DEFAULT_TYPE
#     ) -> tuple[int, str, bool, bool]:
#     message = update.message
#     chat_id = message.chat.id
#     chat_type = message.chat.type
#     is_direct_message = chat_type == 'private'
    
#     bot_username = (await context.bot.get_me()).username

#     is_bot_mentioned = False
#     if message.entities:
#         for entity in message.entities:
#             if entity.type == 'mention' and message.text[entity.offset:entity.offset + entity.length].lower() == f"@{bot_username.lower()}":
#                 is_bot_mentioned = True
#                 break

#     is_replied_to_bot = message.reply_to_message and message.reply_to_message.from_user.username == bot_username

#     is_bot_mentioned_or_replied = is_bot_mentioned or is_replied_to_bot
    
#     return chat_id, chat_type, is_direct_message, is_bot_mentioned_or_replied

# def get_user_info(update:Update) -> tuple[int, str, str, str, str]:
#     message = update.message
#     user_id = message.from_user.id
#     user_name = message.from_user.username

#     first_name = message.from_user.first_name or ""
#     last_name = message.from_user.last_name or ""
#     full_name = f"{first_name} {last_name}".strip()

#     return user_id, user_name, first_name, last_name, full_name


# def remove_bot_mentions(
#         message_text: str, 
#         bot_username: str
#     ) -> str:
#     """
#     Removes all mentions of the bot's username (@bot_username) from the message.
    
#     :param message_text: The text of the message.
#     :param bot_username: The bot's username (without '@').
#     :return: The message with all bot mentions removed.
#     """
#     # Create a regex pattern to match the bot mention with word boundaries
#     bot_mention_pattern = rf"\s*@{re.escape(bot_username)}\b"
    
#     # Remove all occurrences of the bot mention (case-insensitive)
#     cleaned_message = re.sub(bot_mention_pattern, "", message_text, flags=re.IGNORECASE).strip()
    
#     # Remove any extra spaces left after mention removal
#     cleaned_message = re.sub(r'\s+', ' ', cleaned_message)
    
#     return cleaned_message
                                        


# long_running_tools = [
#     "txt2vid",
#     "style_mixing",
#     "img2vid",
#     "vid2vid",
#     "video_upscale",
#     "vid2vid_sdxl",
#     "lora_trainer",
#     "animate_3D",
#     "reel",
#     "story",
# ]

# video_tools = [
#     "animate_3D",
#     "txt2vid",
#     "img2vid",
#     "vid2vid_sdxl",
#     "style_mixing",
#     "video_upscaler",
#     "reel",
#     "story",
#     "lora_trainer",
# ]

# hour_timestamps = {}
# day_timestamps = {}

# HOUR_IMAGE_LIMIT = 50
# HOUR_VIDEO_LIMIT = 10
# DAY_IMAGE_LIMIT = 200
# DAY_VIDEO_LIMIT = 40

# def user_over_rate_limits(user_id):
#     if user_id not in hour_timestamps:
#         hour_timestamps[user_id] = []
#     if user_id not in day_timestamps:
#         day_timestamps[user_id] = []

#     hour_timestamps[user_id] = [
#         t for t in hour_timestamps[user_id] if time.time() - t["time"] < 3600
#     ]
#     day_timestamps[user_id] = [
#         t for t in day_timestamps[user_id] if time.time() - t["time"] < 86400
#     ]

#     hour_video_tool_calls = len(
#         [t for t in hour_timestamps[user_id] if t["tool"] in video_tools]
#     )
#     hour_image_tool_calls = len(
#         [t for t in hour_timestamps[user_id] if t["tool"] not in video_tools]
#     )

#     day_video_tool_calls = len(
#         [t for t in day_timestamps[user_id] if t["tool"] in video_tools]
#     )
#     day_image_tool_calls = len(
#         [t for t in day_timestamps[user_id] if t["tool"] not in video_tools]
#     )

#     if (
#         hour_video_tool_calls >= HOUR_VIDEO_LIMIT
#         or hour_image_tool_calls >= HOUR_IMAGE_LIMIT
#     ):
#         return True
#     if (
#         day_video_tool_calls >= DAY_VIDEO_LIMIT
#         or day_image_tool_calls >= DAY_IMAGE_LIMIT
#     ):
#         return True
#     return False



# class EdenTG:
#     def __init__(self, token: str) -> None:
#         self.token = token
#         api_urls = EdenApiUrls(
#             api_url=os.getenv("EDEN_API_URL") or "http://localhost:5050",
#             tools_api_url=os.getenv("EDEN_TOOLS_API_URL") or "http://127.0.0.1:8000",
#         )
#         self.eden_client = EdenClient(api_urls=api_urls)

#     def start(
#             update: Update, 
#             context: ContextTypes.DEFAULT_TYPE
#         ) -> None:
#         update.message.reply_text('Hello! I am your asynchronous bot.')

#     async def echo(
#             update: Update, 
#             context: ContextTypes.DEFAULT_TYPE
#         ) -> None:
#         chat_id, chat_type, is_direct_message, is_bot_mentioned_or_replied = await handler_mention_type(update, context)
#         user_id, user_name, first_name, last_name, full_name = get_user_info(update) 
#         if update.message.photo:
#             content_type = "photo"
#             photo = update.message.photo[-1]
#             photo_file = await photo.get_file()
#             photo_url = photo_file.file_path
#             print(f"image ulr: {photo_url}")
#         elif update.message.text:
#             content_type = "text"
#             message_text = update.message.text
#         else:
#             print("others")
#             content_type = "unsupported content type"

#         if content_type == "text":
#             bot_username = (await context.bot.get_me()).username
#             message_text = remove_bot_mentions(message_text, bot_username)

#             chat_message = {
#                 "name": user_name,
#                 "content": message_text,
#                 "attachments": [],
#                 "settings": {}
#             }
#             print(f"*******************************************************************{message_text}")
#             media_url = bot_response(message_text)
            
#             if is_direct_message:
#                 await context.bot.send_photo(chat_id=chat_id, photo=media_url)
#             elif is_bot_mentioned_or_replied:
#                 await context.bot.send_photo(chat_id=chat_id, photo=media_url)
#             else:
#                 return

# def main(
#     env:str,
# ) -> None:
#     load_dotenv(env)
#     bot_token = os.getenv("TELEGRAM_TOKEN")

#     application = ApplicationBuilder().token(bot_token).build()
#     eden_bot = EdenTG(bot_token)

#     # Add handlers
#     application.add_handler(CommandHandler("start", eden_bot.start))
#     application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, eden_bot.echo))
#     application.add_handler(MessageHandler(filters.PHOTO, eden_bot.echo))  # Add this line to handle photos

#     # Add error handler
#     application.add_error_handler(error_handler)

#     # Start polling
#     application.run_polling()

# if __name__ == '__main__':
#     parser = argparse.ArgumentParser(description="MarsBot")
#     parser.add_argument("--env", help="Path to the .env file to load", default=".env")
#     args = parser.parse_args()
#     main(args.env)


import os
import argparse
import json
import re
import time
from dotenv import load_dotenv
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from sdk import bot_response
from eden.client import EdenClient
from eden.client import EdenApiUrls

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error("Exception while handling an update:", exc_info=context.error)

async def handler_mention_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> tuple[int, str, bool, bool]:
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

    return chat_id, chat_type, is_direct_message, is_bot_mentioned, is_replied_to_bot

def get_user_info(update: Update) -> tuple[int, str, str, str, str]:
    message = update.message
    user_id = message.from_user.id
    user_name = message.from_user.username

    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""
    full_name = f"{first_name} {last_name}".strip()

    return user_id, user_name, first_name, last_name, full_name


def remove_bot_mentions(message_text: str, bot_username: str) -> str:
    """
    Removes all mentions of the bot's username (@bot_username) from the message.
    
    :param message_text: The text of the message.
    :param bot_username: The bot's username (without '@').
    :return: The message with all bot mentions removed.
    """
    # Create a regex pattern to match the bot mention with word boundaries
    bot_mention_pattern = rf"\s*@{re.escape(bot_username)}\b"
    
    # Remove all occurrences of the bot mention (case-insensitive)
    cleaned_message = re.sub(bot_mention_pattern, "", message_text, flags=re.IGNORECASE).strip()
    
    # Remove any extra spaces left after mention removal
    cleaned_message = re.sub(r'\s+', ' ', cleaned_message)
    
    return cleaned_message

long_running_tools = [
    "txt2vid", "style_mixing", "img2vid", "vid2vid", "video_upscale", 
    "vid2vid_sdxl", "lora_trainer", "animate_3D", "reel", "story"
]

video_tools = [
    "animate_3D", "txt2vid", "img2vid", "vid2vid_sdxl", "style_mixing", 
    "video_upscaler", "reel", "story", "lora_trainer"
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

async def sendResult(
        message_type:str,
        chat_id:int,
        media_url:str,
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
    if message_type == "dm":
        print("direct message")
        await context.bot.send_photo(chat_id=chat_id, photo=media_url)
    elif message_type == "mention":
        print("mention")
        await context.bot.send_photo(chat_id=chat_id, photo=media_url)
    elif message_type == "reply":
        print("reply")
        await context.bot.send_photo(chat_id=chat_id, photo=media_url)
    else:
        return



class EdenTG:
    def __init__(self, token: str) -> None:
        self.token = token
        api_urls = EdenApiUrls(
            api_url=os.getenv("EDEN_API_URL") or "http://localhost:5050",
            tools_api_url=os.getenv("EDEN_TOOLS_API_URL") or "http://127.0.0.1:8000",
        )
        self.eden_client = EdenClient(stage = False)#(api_urls=api_urls)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("Hello! I am your asynchronous bot.")

    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id, chat_type, is_direct_message, is_bot_mentioned, is_replied_to_bot = await handler_mention_type(update, context)
        user_id, user_name, first_name, last_name, full_name = get_user_info(update)
        
        if is_direct_message:
            message_type = "dm"
        elif is_bot_mentioned:
            message_type = "mention"
        elif is_replied_to_bot:
            message_type = "reply"  
        else:
            return

        if update.message.photo:
            content_type = "photo"
            photo = update.message.photo[-1]
            photo_file = await photo.get_file()
            photo_url = photo_file.file_path
            print(f"Image URL: {photo_url}")
        elif update.message.text:
            content_type = "text"
            message_text = update.message.text
        else:
            content_type = "unsupported content type"

        if content_type == "text":
            bot_username = (await context.bot.get_me()).username
            message_text = remove_bot_mentions(message_text, bot_username)

            chat_message = {
                "name": user_name,
                "content": message_text,
                "attachments": [],
                "settings": {}
            }
            thread_id = self.eden_client.get_or_create_thread("test thread name")
            print(f"*******************************************************************{thread_id}")


            async for response in self.eden_client.async_discord_chat(
                chat_message, thread_id, chat_id
            ):
                print("THE RESPONSE", response)
            print(f"*******************************************************************{message_text}")
            # media_url = bot_response(message_text)
            # print(media_url)
            # await sendResult(message_type, chat_id, media_url, context)
           

def main(env: str) -> None:
    load_dotenv(env)
    bot_token = os.getenv("TELEGRAM_TOKEN")

    application = ApplicationBuilder().token(bot_token).build()
    eden_bot = EdenTG(bot_token)

    # Add handlers
    application.add_handler(CommandHandler("start", eden_bot.start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, eden_bot.echo))
    application.add_handler(MessageHandler(filters.PHOTO, eden_bot.echo))  # Add this line to handle photos

    # Add error handler
    application.add_error_handler(error_handler)

    # Start polling
    application.run_polling()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Eden Telegram Bot")
    parser.add_argument("--env", help="Path to the .env file to load", default=".env")
    args = parser.parse_args()
    main(args.env)


