from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

# ربات در حالت bot اجرا بشه، نه user
app = Client(
    "BoxOfficeUploaderBot",  # این اسم باید ثابت بمونه
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# اینجا ربات رو استارت کن
if __name__ == "__main__":
    print("Starting bot...")
    app.run()
