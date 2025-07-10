# handlers/start_handler.py
from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.command("start"))
async def start_handler(client: Client, message: Message):
    await message.reply("✅ ربات آنلاین و سالمه!")
