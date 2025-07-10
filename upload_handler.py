from pyrogram import filters, Client
from pyrogram.types import Message
from config import ADMIN_IDS
from database import save_file

upload_sessions = {}

@Client.on_message(filters.command("upload") & filters.user(ADMIN_IDS))
async def start_upload(client: Client, message: Message):
    user_id = message.from_user.id
    upload_sessions[user_id] = {
        "state": "awaiting_film_id",
        "film_id": None,
        "files": []
    }
    await message.reply("🎬 لطفاً شناسه (Film ID) فیلم را ارسال کنید:")

@Client.on_message((filters.video | filters.document) & filters.user(ADMIN_IDS))
async def handle_file(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id not in upload_sessions:
        return
    session = upload_sessions[user_id]

    if session["state"] == "awaiting_file":
        file_id = message.video.file_id if message.video else message.document.file_id
        session["files"].append({
            "file_id": file_id,
            "quality": "",
            "caption": ""
        })
        session["state"] = "awaiting_quality"
        await message.reply("📶 لطفاً کیفیت فایل را وارد کنید (مثلاً 720p):")

@Client.on_message(filters.text & filters.user(ADMIN_IDS))
async def handle_text_steps(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id not in upload_sessions:
        return

    session = upload_sessions[user_id]
    state = session["state"]
    text = message.text.strip()

    if state == "awaiting_film_id":
        session["film_id"] = text
        session["state"] = "awaiting_file"
        await message.reply("📁 حالا لطفاً فایل فیلم را ارسال کنید:")

    elif state == "awaiting_quality":
        session["files"][-1]["quality"] = text
        session["state"] = "awaiting_caption"
        await message.reply("📝 لطفاً کپشن کوتاه فایل را وارد کنید:")

    elif state == "awaiting_caption":
        session["files"][-1]["caption"] = text
        session["state"] = "awaiting_more_files"
        await message.reply("📌 آیا فایل دیگری برای این فیلم دارید؟ (بله / خیر)")

    elif state == "awaiting_more_files":
        if text.lower() in ["بله", "yes", "آره", "اره"]:
            session["state"] = "awaiting_file"
            await message.reply("📁 لطفاً فایل بعدی را ارسال کنید:")
        elif text.lower() in ["خیر", "no", "نه"]:
            for f in session["files"]:
                await save_file(session["film_id"], f["file_id"], f["quality"], f["caption"])

            bot_username = (await client.get_me()).username
            deep_link = f"https://t.me/{bot_username}?start={session['film_id']}"

            await message.reply(
                f"✅ همه فایل‌ها ذخیره شدند.\n\n📎 لینک اشتراک‌گذاری:\n[برای دانلود این فیلم کلیک کنید]({deep_link})",
                parse_mode="markdown"
            )
            del upload_sessions[user_id]
        else:
            await message.reply("❗ لطفاً فقط «بله» یا «خیر» پاسخ دهید.")
