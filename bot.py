import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import MongoDBClient
from config import API_ID, API_HASH, BOT_TOKEN, ADMIN_IDS, CHANNELS_TO_CHECK
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Client("BoxOfficeSuperBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
db = MongoDBClient()

# پیام خوش آمدگویی همراه با عکس و دکمه‌ها
WELCOME_IMAGE = "https://i.imgur.com/HBYNljO.png"  # آدرس عکس خوش آمدگویی

async def check_membership(user_id):
    for channel in CHANNELS_TO_CHECK:
        try:
            member = await app.get_chat_member(channel, user_id)
            if member.status in ("left", "kicked"):
                return False
        except Exception:
            return False
    return True

@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    user_id = message.from_user.id
    if not await check_membership(user_id):
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("عضویت در کانال‌ها", url="https://t.me/BoxOfficeMoviiie")]]
        )
        await message.reply("برای استفاده از ربات لطفا ابتدا در کانال‌های ما عضو شوید.", reply_markup=keyboard)
        return

    await message.reply_photo(
        WELCOME_IMAGE,
        caption="سلام! خوش آمدید به ربات BoxOffice. برای مشاهده فیلم‌ها از لینک‌های اشتراک‌گذاری استفاده کنید.",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("کانال رسمی", url="https://t.me/BoxOfficeMoviiie")]]
        )
    )

# فقط ادمین‌ها می‌توانند آپلود کنند
@app.on_message(filters.private & filters.media & filters.user(ADMIN_IDS))
async def upload_handler(client, message):
    chat_id = message.chat.id
    await message.reply("✅ فایل دریافت شد. لطفا اطلاعات فیلم را وارد کنید.")
    # مرحله ۱: دریافت عنوان فیلم
    title_msg = await app.ask(chat_id, "لطفا عنوان فیلم یا سریال را وارد کنید:")
    title = title_msg.text.strip()
    
    # مرحله ۲: دریافت کیفیت فیلم
    quality_msg = await app.ask(chat_id, "کیفیت فیلم را وارد کنید (مثال: 720p, 1080p):")
    quality = quality_msg.text.strip()
    
    # مرحله ۳: دریافت توضیحات (اختیاری)
    caption_msg = await app.ask(chat_id, "توضیحات یا کپشن فیلم (اختیاری):")
    caption = caption_msg.text.strip() if caption_msg.text else ""

    # ذخیره فایل در دیتابیس
    file_id = message.document.file_id if message.document else (
        message.video.file_id if message.video else None
    )
    if not file_id:
        await message.reply("⚠️ فایل ویدئویی پیدا نشد، لطفا دوباره تلاش کنید.")
        return

    film_id = db.generate_film_id(title)
    # ذخیره در دیتابیس
    db.add_file(film_id, file_id, title, quality, caption)

    # پرسش درباره آپلود فایل‌های دیگر برای همین فیلم
    more_msg = await app.ask(chat_id, "آیا فایل ویدئویی دیگری برای این فیلم دارید؟ (بله/خیر):")
    if more_msg.text.lower() == "بله":
        await message.reply("لطفا فایل بعدی را ارسال کنید.")
        # می‌توان به صورت بازگشتی یا حلقه ادامه داد (توسعه می‌شود)
    else:
        # تمام فایل‌ها دریافت شد، لینک اشتراک‌گذاری ساخته شود
        link = f"https://t.me/BoxOfficeSuperBot?start={film_id}"
        await message.reply(f"✅ آپلود کامل شد!\nلینک اشتراک‌گذاری:\n{link}")

@app.on_message(filters.command("start") & filters.private & filters.regex(r"^get_[\w\d]+"))
async def start_with_film(client, message):
    # پردازش لینک با فیلم آی‌دی
    film_id = message.text.split("_", 1)[1]
    files = db.get_files(film_id)
    if not files:
        await message.reply("فیلمی با این شناسه یافت نشد.")
        return
    # ارسال فایل‌ها با دکمه دانلود
    for f in files:
        caption = f"{f['title']} - {f['quality']}\n{f['caption']}"
        btn = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🎬 دانلود", callback_data=f"download_{f['file_id']}")]]
        )
        await message.reply_document(f['file_id'], caption=caption, reply_markup=btn)
    # پیام هشدار حذف بعد از ۳۰ ثانیه
    await message.reply("⚠️ فایل‌ها پس از ۳۰ ثانیه حذف خواهند شد. لطفا ذخیره کنید.")

@app.on_callback_query(filters.regex(r"^download_"))
async def download_callback(client, callback_query):
    file_id = callback_query.data.split("_", 1)[1]
    await callback_query.message.reply_document(file_id)
    await callback_query.answer("فایل ارسال شد. لطفا ذخیره کنید.")

if __name__ == "__main__":
    app.run()
