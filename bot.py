import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
from urllib.parse import quote_plus

# مقادیر ثابت و محرمانه (لطفاً این مقادیر رو محفوظ نگه دار)
API_ID = 26438691
API_HASH = "b9a6835fa0eea6e9f8a87a320b3ab1ae"
TOKEN = "8031070707:AAEf5KDsmxL2x1_iZ_A1PgrGuqPL29TaW8A"
ADMIN_ID = 7872708405

# اطلاعات اتصال به MongoDB (کلمه عبور با urlencode شده)
MONGO_USERNAME = "smilymeh"
MONGO_PASSWORD = "M@hdi1985!"
MONGO_PASS_ENCODED = quote_plus(MONGO_PASSWORD)
MONGO_URI = f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASS_ENCODED}@cluster0.ve2f0zq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

mongo_client = MongoClient(MONGO_URI)
db = mongo_client["boxoffice_db"]
files_collection = db["files"]

REQUIRED_CHANNELS = [
    "BoxOffice_Animation",
    "BoxOfficeMoviiie",
    "BoxOffice_Irani",
    "BoxOfficeGoftegu"
]

upload_data = {}

app = Client(
    "boxoffice_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN
)

WELCOME_IMAGE = "https://i.imgur.com/HBYNljO.png"


async def user_is_subscribed(client, user_id: int) -> bool:
    """بررسی عضویت کاربر در همه کانال‌های لازم"""
    for chan in REQUIRED_CHANNELS:
        try:
            member = await client.get_chat_member(chat_id=chan, user_id=user_id)
            if member.status in ("left", "kicked"):
                return False
        except Exception:
            return False
    return True


def get_subscribe_buttons():
    buttons = [[
        InlineKeyboardButton(f"عضویت در @{chan}", url=f"https://t.me/{chan}")
    ] for chan in REQUIRED_CHANNELS]
    buttons.append([InlineKeyboardButton("✅ عضو شدم", callback_data="check_subscription")])
    return InlineKeyboardMarkup(buttons)


@app.on_message(filters.private & filters.command("start"))
async def start_handler(client, message):
    user_id = message.from_user.id
    args = message.text.split()

    # اگر لینک با شناسه فیلم شروع شده
    if len(args) == 2:
        film_id = args[1]

        if not await user_is_subscribed(client, user_id):
            await message.reply(
                "❗️ لطفاً ابتدا در همه کانال‌های زیر عضو شوید و سپس روی دکمه '✅ عضو شدم' بزنید:",
                reply_markup=get_subscribe_buttons()
            )
            return

        files = list(files_collection.find({"film_id": film_id}))
        if not files:
            await message.reply("❌ هیچ فایلی با این شناسه یافت نشد.")
            return

        sent_msgs = []
        for file in files:
            caption = f"{file['caption']} | کیفیت: {file['quality']}"
            sent = await client.send_video(message.chat.id, file['file_id'], caption=caption)
            sent_msgs.append(sent)

        warning_msg = await message.reply("⚠️ فایل‌ها تا ۳۰ ثانیه دیگر حذف می‌شوند، لطفاً ذخیره کنید.")
        sent_msgs.append(warning_msg)

        await asyncio.sleep(30)
        for msg in sent_msgs:
            try:
                await msg.delete()
            except:
                pass
        return

    # پیام خوش آمد گویی به همراه عکس و دکمه‌های عضویت
    await client.send_photo(
        chat_id=message.chat.id,
        photo=WELCOME_IMAGE,
        caption=(
            "🎬 به ربات BoxOffice خوش آمدید!\n\n"
            "برای دریافت فایل‌ها، شناسه فیلم را به صورت زیر ارسال کنید:\n"
            "/start film_id\n\n"
            "ابتدا باید در کانال‌های زیر عضو شوید و سپس روی دکمه '✅ عضو شدم' کلیک کنید."
        ),
        reply_markup=get_subscribe_buttons()
    )


@app.on_callback_query(filters.regex("^check_subscription$"))
async def check_subscription(client, callback_query):
    user_id = callback_query.from_user.id

    if await user_is_subscribed(client, user_id):
        await callback_query.answer("✅ عضویت شما تایید شد!", show_alert=True)
        await callback_query.message.edit(
            "🎉 تبریک! شما عضو همه کانال‌ها هستید.\n\n"
            "لطفاً شناسه فیلم مورد نظر را با دستور زیر ارسال کنید:\n"
            "/start film_id"
        )
    else:
        await callback_query.answer("❌ هنوز عضو همه کانال‌ها نیستید!", show_alert=True)
        await callback_query.message.edit(
            "❗️ لطفاً ابتدا در همه کانال‌های زیر عضو شوید و سپس روی دکمه '✅ عضو شدم' کلیک کنید:",
            reply_markup=get_subscribe_buttons()
        )


@app.on_message(filters.private & filters.video)
async def video_handler(client, message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        await message.reply("⚠️ فقط ادمین اجازه ارسال ویدیو را دارد.")
        return

    video_file_id = message.video.file_id
    upload_data[user_id] = {"video_file_id": video_file_id, "step": "awaiting_film_id"}
    await message.reply("✅ ویدیو دریافت شد.\nلطفاً شناسه عددی فیلم را وارد کنید:")


@app.on_message(filters.private & filters.text)
async def text_handler(client, message):
    user_id = message.from_user.id

    # اگر پیام ادمین نبود فقط استارت رو قبول کن
    if user_id != ADMIN_ID:
        if message.text.startswith("/start"):
            await start_handler(client, message)
        else:
            await message.reply("⚠️ لطفاً از لینک‌های اختصاصی استفاده کنید یا /start را بزنید.")
        return

    if user_id not in upload_data:
        await message.reply("⚠️ لطفاً ابتدا ویدیو ارسال کنید.")
        return

    data = upload_data[user_id]

    if data["step"] == "awaiting_film_id":
        data["film_id"] = message.text.strip()
        data["step"] = "awaiting_caption"
        await message.reply("لطفاً کپشن کوتاه برای فیلم وارد کنید:")
        return

    if data["step"] == "awaiting_caption":
        data["caption"] = message.text.strip()
        data["step"] = "awaiting_quality"
        await message.reply("لطفاً کیفیت فیلم را وارد کنید (مثلاً 360p، 720p):")
        return

    if data["step"] == "awaiting_quality":
        data["quality"] = message.text.strip()

        # ذخیره در دیتابیس
        files_collection.insert_one({
            "film_id": data["film_id"],
            "file_id": data["video_file_id"],
            "caption": data["caption"],
            "quality": data["quality"]
        })

        # ساخت لینک دیپ لینک اختصاصی
        bot_username = (await app.get_me()).username
        deep_link = f"https://t.me/{bot_username}?start={data['film_id']}"

        await message.reply(
            f"✅ فایل با موفقیت ذخیره شد.\n"
            f"🎬 شناسه فیلم: {data['film_id']}\n"
            f"📽 کیفیت: {data['quality']}\n\n"
            f"🔗 لینک اشتراک:\n{deep_link}"
        )
        upload_data.pop(user_id)


if __name__ == "__main__":
    print("Bot is starting...")
    app.run()
