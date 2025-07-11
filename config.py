import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("TOKEN")
MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB = os.getenv("MONGO_DB")

# لیست آی‌دی‌های ادمین
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))

# لیست کانال‌هایی که عضویت در آن‌ها اجباری است
REQUIRED_CHANNELS = [
    {"id": -1002601782167, "username": "BoxOfficeMoviiie"},
    {"id": -1002573288143, "username": "BoxOffice_Animation"},
    {"id": -1002422139602, "username": "BoxOffice_Irani"},
    {"id": -1002535507643, "username": "BoxOfficeGAP"},
]

WELCOME_IMAGE_URL = "https://i.imgur.com/HBYNljO.png"
