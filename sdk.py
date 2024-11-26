from eden_sdk.EdenClient import EdenClient
from dotenv import load_dotenv
import os

load_dotenv()

eden = EdenClient(
    api_key=os.getenv("EDEN_API_KEY"),
    api_secret=os.getenv("EDEN_API_SECRET")
)

def bot_response(text):
    config = {
        "text_input": text,
    }
    urls = eden.create(generator_name='create', config=config)
    return urls[0]
