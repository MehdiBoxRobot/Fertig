from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

app = Client(
    "BoxOfficeBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN  # این خط باید اضافه شود
)

@app.on_message()
async def handler(client, message):
    await message.reply("ربات آماده است.")

if __name__ == "__main__":
    app.run()
