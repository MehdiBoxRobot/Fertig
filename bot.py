from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN
import upload_handler
import start_handler

app = Client("BoxOfficeBot", api_id=API_ID, api_hash=API_HASH
