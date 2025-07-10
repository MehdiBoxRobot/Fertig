from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

files_col = db["files"]
stats_col = db["stats"]  # برای آمار ویو، دانلود، اشتراک


async def save_file(film_id, file_id, quality, caption):
    """ذخیره فایل در دیتابیس"""
    existing = files_col.find_one({"film_id": film_id, "file_id": file_id})
    if existing:
        return False
    files_col.insert_one({
        "film_id": film_id,
        "file_id": file_id,
        "quality": quality,
        "caption": caption
    })
    # آمار اولیه
    stats_col.update_one(
        {"film_id": film_id},
        {"$setOnInsert": {"views": 0, "downloads": 0, "shares": 0}},
        upsert=True
    )
    return True

async def get_files_by_film_id(film_id):
    return list(files_col.find({"film_id": film_id}))

async def increment_stat(film_id, stat_type):
    """stat_type can be 'views', 'downloads', or 'shares'"""
    if stat_type not in ['views', 'downloads', 'shares']:
        return
    stats_col.update_one({"film_id": film_id}, {"$inc": {stat_type: 1}})

async def get_stats(film_id):
    stats = stats_col.find_one({"film_id": film_id})
    if not stats:
        return {"views": 0, "downloads": 0, "shares": 0}
    return {k: stats.get(k, 0) for k in ["views", "downloads", "shares"]}
