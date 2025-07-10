import asyncio
from pyrogram import Client, filters
from config import API_ID, API_HASH, BOT_TOKEN, ADMIN_IDS
import handlers.upload_handler
import handlers.callback_handler
import handlers.user_handler
import handlers.subscription_handler

app = Client("boxoffice_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def main():
    print("Bot is starting...")
    await app.start()
    print("Bot started!")
    await idle()  # keeps the bot running

if __name__ == "__main__":
    import logging
    from pyrogram import idle

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )
    asyncio.run(main())
