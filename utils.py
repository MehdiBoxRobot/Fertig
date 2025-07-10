def make_caption(film_id, files, stats):
    """
    ساخت کپشن حرفه‌ای با لینک‌های Markdown و آمار جدا
    files = list of dicts: [{file_id, quality, caption}]
    stats = dict with views, downloads, shares
    """

    caption_lines = []
    caption_lines.append("🎬 فیلم شما آماده است:\n")

    for f in files:
        # لینک دانلود به شکل متن کلیک‌خور:
        caption_lines.append(
            f"📥 [{f['caption']} ({f['quality']})](https://t.me/YourBotUsername?start={film_id})"
        )

    caption_lines.append("\n📊 آمار:\n")
    caption_lines.append(f"👁️‍🗨️ بازدیدها: {stats.get('views', 0)}")
    caption_lines.append(f"⬇️ دانلودها: {stats.get('downloads', 0)}")
    caption_lines.append(f"🔗 اشتراک‌گذاری: {stats.get('shares', 0)}")
    caption_lines.append("\n⚠️ پیام‌ها پس از ۳۰ ثانیه حذف خواهند شد، لطفاً ذخیره کنید.")

    return "\n".join(caption_lines)
