from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN
import handlers.upload_handler
import handlers.user_handler
import handlers.callback_handler

app = Client("boxoffice_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

if __name__ == "__main__":
    print("Bot is starting...")
    app.run()
