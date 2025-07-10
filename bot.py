from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

app = Client(
    "BoxOfficeBot",  # اسم پروژه. مهم نیست چی باشه ولی باید ثابت بمونه
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN  # این خط باعث میشه Pyrogram وارد حالت Bot بشه
)

@app.on_message()
async def start_handler(client, message):
    await message.reply("✅ ربات آنلاین و سالمه!")

if __name__ == "__main__":
    print("🔥 Bot is starting...")
    app.run()
