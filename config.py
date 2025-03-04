import os
import json

class Config:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_API", '1612943357:AAGMpBR8UBQqvPFKotlVt5UyEV3j3x74_rs')
        self.download_directory = os.getenv("DOWNLOAD_FOLDER", 'Download')
        self.storage_directory = os.path.join(self.download_directory, "from_telegram_loader")

        self.white_users_list = json.loads(os.getenv("WHITE_USERS_LIST", '[216757486]'))

        os.makedirs(self.download_directory, exist_ok=True)
        os.makedirs(self.storage_directory, exist_ok=True)

        self.directories = {
            "photo": os.path.join(self.storage_directory, "photos"),
            "audio": os.path.join(self.storage_directory, "audio"),
            "voice": os.path.join(self.storage_directory, "voice"),
            "video": os.path.join(self.storage_directory, "videos"),
            "animation": os.path.join(self.storage_directory, "animations"),
            "sticker": os.path.join(self.storage_directory, "stickers"),
            "document": os.path.join(self.storage_directory, "documents"),
            "doc_photo": os.path.join(self.storage_directory, "Doc_Photos"),
            "torrent": os.path.join(self.download_directory, "torrents"),
            "sirko_logs": os.path.join(self.download_directory, "sirko_logs"),

        }
        self.extensions = {
            "photo": ".jpg",
            "audio": ".mp3",
            "voice": ".ogg",
            "video": ".mp4",
            "animation": ".gif",
            "sticker": ".webp",
            "document": ".pdf",
            "doc_photo": ".jpg",
            "torrent": ".torrent",
        }
        for folder in self.directories.values():
            os.makedirs(folder, exist_ok=True)