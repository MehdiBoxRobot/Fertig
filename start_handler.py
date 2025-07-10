from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import get_files_by_film_id, increment_stat
from check_subscription import check_user_subscriptions
from config import CHANNELS

@Client.on_message(filters.command("start"))
async def start(client: Client, message):
    args = message.command[1:]  # بعد از /start
    if not args:
        await message.reply("👋 سلام! برای دریافت فیلم لطفاً لینک دانلود را از کانال‌ها دریافت کنید.")
        return

    film_id = args[0]

    # چک عضویت
    is_subscribed, channel = await check_user_subscriptions(client, message.from_user.id)
    if not is_subscribed:
        await message.reply(
            f"❗ لطفاً ابتدا در کانال [{channel}](https://t.me/{channel}) عضو شوید و دوباره تلاش کنید.",
            parse_mode="markdown"
        )
        return

    files = await get_files_by_film_id(film_id)
    if not files:
        await message.reply("❌ فیلم مورد نظر پیدا نشد.")
        return

    await increment_stat(film_id, "views")

    # ارسال فایل‌ها با کپشن و دکمه دانلود
    for f in files:
        caption = f["caption"]
        file_id = f["file_id"]
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🎬 دانلود", callback_data=f"download|{file_id}")]]
        )
        await client.send_cached_media(message.chat.id, file_id, caption=caption, reply_markup=keyboard)

    await message.reply("⚠️ این فایل‌ها پس از ۳۰ ثانیه حذف خواهند شد. لطفاً ذخیره کنید.")

@Client.on_callback_query()
async def callback_query(client, callback_query):
    data = callback_query.data
    if data.startswith("download|"):
        file_id = data.split("|")[1]
        await increment_stat(None, "downloads")  # یا می‌توان آیدی فیلم را از فایل استخراج کرد
        await client.send_cached_media(callback_query.from_user.id, file_id)
        await callback_query.answer("🎬 فایل دانلود شد. لطفاً ذخیره کنید.")

        # حذف پیام بعد از 30 ثانیه
        import asyncio
        await asyncio.sleep(30)
        await client.delete_messages(callback_query.message.chat.id, callback_query.message.message_id)
