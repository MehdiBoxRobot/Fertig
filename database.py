from pymongo import MongoClient, errors
from config import MONGO_URI, MONGO_DB
import logging

# تنظیم لاگر
logger = logging.getLogger("MongoDB")
logger.setLevel(logging.INFO)

# اتصال به دیتابیس با مدیریت خطا
try:
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    mongo_client.server_info()  # بررسی اتصال
    db = mongo_client[MONGO_DB]
    logger.info("✅ MongoDB connection established successfully.")
except errors.ServerSelectionTimeoutError as err:
    logger.error(f"❌ MongoDB connection failed: {err}")
    db = None

# اگر اتصال موفق بود، کالکشن‌ها رو تعریف کن
if db:
    files_collection = db["files"]
    users_collection = db["users"]
    logs_collection = db["logs"]
else:
    files_collection = users_collection = logs_collection = None
