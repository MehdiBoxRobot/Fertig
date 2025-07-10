from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

app = Client(
    name="bot",  # فقط "bot" بذار برای جلوگیری از .session اضافی
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message()
async def hello_handler(client, message):
    await message.reply("✅ Bot is working!")

if __name__ == "__main__":
    print("🔥 Bot is starting...")
    app.run()
