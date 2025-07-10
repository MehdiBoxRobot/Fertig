import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaVideo, InputMediaPhoto
from pymongo import MongoClient
from urllib.parse import quote_plus

# تنظیمات مهم
TOKEN = "8031070707:AAEf5KDsmxL2x1_iZ_A1PgrGuqPL29TaW8A"
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))
  # آیدی ادمین‌ها

username = "smilymeh"
password = "M@hdi1985!"
password_encoded = quote_plus(password)
MONGO_URI = f"mongodb+srv://{username}:{password_encoded}@cluster0.ve2f0zq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

mongo_client = MongoClient(MONGO_URI)
db = mongo_client["boxoffice_db"]
files_collection = db["files"]

REQUIRED_CHANNELS = [
    "BoxOffice_Animation",
    "BoxOfficeMoviiie",
    "BoxOffice_Irani",
    "BoxOfficeGoftegu"
]

upload_sessions = {}  # داده موقت آپلود (ادمین‌ها)
app = Client("boxoffice_bot", bot_token=TOKEN)


# بررسی عضویت کاربر توی همه کانال‌ها
async def user_is_subscribed(client, user_id):
    for channel in REQUIRED_CHANNELS:
        try:
            member = await client.get_chat_member(channel, user_id)
            if member.status in ("left", "kicked"):
                return False
        except Exception:
            return False
    return True


# دکمه‌های عضویت
def get_subscribe_buttons():
    buttons = [[InlineKeyboardButton(f"عضویت در @{chan}", url=f"https://t.me/{chan}")] for chan in REQUIRED_CHANNELS]
    buttons.append([InlineKeyboardButton("✅ عضو شدم", callback_data="check_subscription")])
    return InlineKeyboardMarkup(buttons)


# خوش آمدگویی با عکس و متن جذاب
@app.on_message(filters.private & filters.command("start"))
async def start_handler(client, message):
    user_id = message.from_user.id
    args = message.text.split()

    if len(args) == 2:
        # استارت با شناسه فیلم: /start film_id
        film_id = args[1]

        if not await user_is_subscribed(client, user_id):
            await message.reply(
                "❗️ لطفاً ابتدا در همه کانال‌های زیر عضو شوید و سپس روی دکمه 'عضو شدم' بزنید:",
                reply_markup=get_subscribe_buttons()
            )
            return

        # بارگذاری فایل‌های مرتبط با فیلم
        files = list(files_collection.find({"film_id": film_id}))
        if not files:
            await message.reply("❌ هیچ فایلی با این شناسه پیدا نشد.")
            return

        sent_messages = []

        # ارسال فایل‌ها به صورت ویدیو با کپشن اختصاصی
        for file in files:
            caption_text = f"{file['caption']} 🎥 کیفیت: {file['quality']}\n\n" \
                           f"🎬 دانلود مستقیم: [دانلود]({file['download_url']})"
            sent = await client.send_video(message.chat.id, file['file_id'], caption=caption_text, parse_mode="markdown")
            sent_messages.append(sent)

        # پیام هشدار حذف بعد 30 ثانیه
        warning_msg = await message.reply("⚠️ فایل‌ها تا ۳۰ ثانیه دیگر حذف خواهند شد، لطفاً آن‌ها را ذخیره کنید.")
        sent_messages.append(warning_msg)

        await asyncio.sleep(30)

        for msg in sent_messages:
            try:
                await msg.delete()
            except:
                pass
        return

    # استارت معمولی (بدون شناسه فیلم)
    welcome_photo_url = "https://i.imgur.com/HBYNljO.png"  # عکس خوش آمدگویی
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


# بررسی دکمه "عضو شدم"
@app.on_callback_query(filters.regex("^check_subscription$"))
async def check_subscription(client, callback_query):
    user_id = callback_query.from_user.id

    if await user_is_subscribed(client, user_id):
        await callback_query.answer("✅ عضویت شما تایید شد!", show_alert=True)
        await callback_query.message.edit(
            "🎉 تبریک! شما عضو همه کانال‌ها هستید.\n\n"
            "از اینکه ما را انتخاب کردید سپاسگزاریم.\n"
            "برای دریافت فایل‌ها، حتماً روی لینک‌های موجود در کپشن فیلم‌ها کلیک کنید."
        )
    else:
        await callback_query.answer("❌ هنوز عضو همه کانال‌ها نیستید!", show_alert=True)
        # نمایش مجدد دکمه‌ها برای عضویت
        await callback_query.message.edit(
            "❗️ لطفاً ابتدا در همه کانال‌های زیر عضو شوید و سپس روی دکمه 'عضو شدم' بزنید:",
            reply_markup=get_subscribe_buttons()
        )


# مدیریت آپلود فایل توسط ادمین
@app.on_message(filters.private & filters.video)
async def handle_video(client, message):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        await message.reply("⚠️ فقط ادمین اجازه ارسال ویدیو دارد.")
        return

    video_file_id = message.video.file_id

    if user_id not in upload_sessions:
        upload_sessions[user_id] = {
            "files": [],
            "qualities": [],
            "step": "awaiting_film_id"
        }

    upload_sessions[user_id]["files"].append(video_file_id)
    await message.reply("✅ ویدیو دریافت شد. لطفاً شناسه عددی فیلم را وارد کنید:")


@app.on_message(filters.private & filters.text)
async def handle_text(client, message):
    user_id = message.from_user.id
    text = message.text.strip()

    if user_id not in ADMIN_IDS:
        # کاربر عادی فقط اجازه start داره
        if text.startswith("/start"):
            await start_handler(client, message)
        else:
            await message.reply("⚠️ لطفاً از لینک‌های اختصاصی استفاده کنید یا /start را بزنید.")
        return

    if user_id not in upload_sessions:
        await message.reply("⚠️ لطفاً ابتدا ویدیو ارسال کنید.")
        return

    session = upload_sessions[user_id]

    # مراحل آپلود ادمین به صورت مرحله‌ای
    if session["step"] == "awaiting_film_id":
        session["film_id"] = text
        session["step"] = "awaiting_caption"
        await message.reply("لطفاً کپشن کوتاه برای فیلم وارد کنید:")
        return

    if session["step"] == "awaiting_caption":
        session["caption"] = text
        session["step"] = "awaiting_quality"
        await message.reply("لطفاً کیفیت فیلم (مثلاً 360p) برای فایل اول وارد کنید:")
        return

    if session["step"] == "awaiting_quality":
        session["qualities"].append(text)
        session["step"] = "awaiting_more_files"
        await message.reply("آیا فایل دیگری برای این فیلم دارید؟ لطفاً پاسخ دهید: بله / خیر")
        return

    if session["step"] == "awaiting_more_files":
        if text.lower() in ["بله", "اره", "yes", "y"]:
            session["step"] = "awaiting_quality"
            await message.reply("لطفاً کیفیت فیلم برای فایل بعدی وارد کنید:")
            return
        elif text.lower() in ["خیر", "نه", "no", "n"]:
            # ذخیره همه فایل‌ها در دیتابیس با لینک دانلود مستقیم
            film_id = session["film_id"]
            caption = session["caption"]
            files = session["files"]
            qualities = session["qualities"]

            bot_username = (await app.get_me()).username

            for idx, file_id in enumerate(files):
                quality = qualities[idx] if idx < len(qualities) else "Unknown"
                download_url = f"https://t.me/{bot_username}?start={film_id}"
                files_collection.insert_one({
                    "film_id": film_id,
                    "file_id": file_id,
                    "caption": caption,
                    "quality": quality,
                    "download_url": download_url
                })

            deep_link = f"https://t.me/{bot_username}?start={film_id}"

            await message.reply(
                f"✅ همه فایل‌ها برای فیلم '{film_id}' ذخیره شدند.\n"
                f"🔗 لینک اشتراک:\n{deep_link}"
            )

            upload_sessions.pop(user_id)
            return
        else:
            await message.reply("لطفاً فقط با «بله» یا «خیر» پاسخ دهید.")
            return
