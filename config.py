import os

API_ID = int(os.getenv("API_ID", "YOUR_API_ID"))
API_HASH = os.getenv("API_HASH", "YOUR_API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "123456789").split(",")))

CHANNELS_TO_CHECK = [
    "@BoxOfficeMoviiie",
    "@BoxOffice_Irani",
    "@BoxOffice_Animation",
    "@BoxOfficeGoftegu"
]
