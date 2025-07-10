import asyncio
import logging
from pyrogram import Client, filters
from config import API_ID, API_HASH, BOT_TOKEN, ADMIN_IDS

logging.basicConfig(level=logging.INFO)
print("🔥 Bot is starting...")

app = Client(
    "BoxOfficeUploaderBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# فقط ادمین‌ها اجازه دارند فایل آپلود کنند
@app.on_message(filters.private & filters.media & filters.user(ADMIN_IDS))
async def handle_upload(client, message):
    await message.reply("✅ فایل دریافت شد. ادامه‌ی مراحل اضافه خواهد شد...")

# دستور ساده برای تست
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply("سلام! ربات با موفقیت اجرا شد ✅")

if __name__ == "__main__":
    app.run()
