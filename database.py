from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
files_collection = db["files"]

async def save_file(film_id, file_id, quality, caption):
    files_collection.insert_one({
        "film_id": film_id,
        "file_id": file_id,
        "quality": quality,
        "caption": caption
    })