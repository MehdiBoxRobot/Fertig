import pymongo
import random
import string

MONGO_URI = "mongodb+srv://your_user:your_password@cluster.mongodb.net/boxoffice?retryWrites=true&w=majority"

class MongoDBClient:
    def __init__(self):
        self.client = pymongo.MongoClient(MONGO_URI)
        self.db = self.client["boxoffice_db"]
        self.films = self.db["films"]

    def generate_film_id(self, title):
        # ساخت شناسه یکتا برای فیلم
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        base = ''.join(e for e in title if e.isalnum()).lower()
        return f"{base}_{suffix}"

    def add_file(self, film_id, file_id, title, quality, caption):
        # اضافه کردن فایل به فیلم (مجموعه فایل‌ها)
        film = self.films.find_one({"film_id": film_id})
        if film:
            self.films.update_one(
                {"film_id": film_id},
                {"$push": {"files": {"file_id": file_id, "quality": quality, "caption": caption}}}
            )
        else:
            self.films.insert_one({
                "film_id": film_id,
                "title": title,
                "files": [{"file_id": file_id, "quality": quality, "caption": caption}]
            })

    def get_files(self, film_id):
        film = self.films.find_one({"film_id": film_id})
        if film:
            return film.get("files", [])
        return []
