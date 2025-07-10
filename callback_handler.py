from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from user_handler import user_is_subscribed, get_subscribe_buttons

@Client.on_callback_query(filters.regex("^check_subscription$"))
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
        await callback_query.message.edit(
            "❗️ لطفاً ابتدا در همه کانال‌های زیر عضو شوید و سپس روی دکمه 'عضو شدم' بزنید:",
            reply_markup=get_subscribe_buttons()
        )
