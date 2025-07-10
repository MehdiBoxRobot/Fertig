import asyncio
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import get_files_by_film_id, increment_stat, get_stats
from config import REQUIRED_CHANNELS

async def user_is_subscribed(client, user_id):
    for channel in REQUIRED_CHANNELS:
        try:
            member = await client.get_chat_member(channel, user_id)
            if member.status in ("left", "kicked"):
                return False
        except Exception:
            return False
    return True

def get_subscribe_buttons():
    buttons = [[InlineKeyboardButton(f"عضویت در @{chan}", url=f"https://t.me/{chan}")] for chan in REQUIRED_CHANNELS]
    buttons.append([InlineKeyboardButton("✅ عضو شدم", callback_data="check_subscription")])
    return InlineKeyboardMarkup(buttons)

@Client.on_message(filters.private & filters.command("start"))
async def start_handler(client, message):
    user_id = message.from_user.id
    args = message.text.split()

    if len(args) == 2:
        film_id = args[1]

        if not await user_is_subscribed(client, user_id):
            await message.reply(
                "❗️ لطفاً ابتدا در همه کانال‌های زیر عضو شوید و سپس روی دکمه 'عضو شدم' بزنید:",
                reply_markup=get_subscribe_buttons()
            )
            return

        files = await get_files_by_film_id(film_id)
        if not files:
            await message.reply("❌ هیچ فایلی با این شناسه پیدا نشد.")
            return

        stats = await get_stats(film_id)
        await increment_stat(film_id, "views")

        sent_messages = []

        bot_username = (await client.get_me()).username
        # ساخت کپشن با لینک شیک و آمار
        from utils import make_caption
        caption = make_caption(film_id, files, stats).replace("YourBotUsername", bot_username)

        for f in files:
            sent = await client.send_video(
                message.chat.id,
                f['file_id'],
                caption=None,
                parse_mode=None
            )
            sent_messages.append(sent)

        warning_msg = await message.reply(caption, parse_mode="markdown")
        sent_messages.append(warning_msg)

        await asyncio.sleep(30)

        for msg in sent_messages:
            try:
                await msg.delete()
            except:
                pass
        return

    # شروع معمولی بدون شناسه فیلم
    welcome_photo_url = "https://i.imgur.com/HBYNljO.png"
    await message.reply_photo(
        welcome_photo_url,
        caption=(
            "🎬 به ربات BoxOffice خوش آمدید!\n\n"
            "برای دریافت فایل، لینک اختصاصی با فرمت زیر را ارسال کنید:\n"
            "/start film_id\n\n"
            "ابتدا باید در کانال‌های زیر عضو شوید:"
        ),
        reply_markup=get_subscribe_buttons()
    )
