import os
import logging
from datetime import datetime
from config import Config

class FileManager:
    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger
    def get_folder_for_media(self, media_type: str):
        return self.config.directories.get(media_type, os.path.join(self.config.storage_directory, "others"))

    def generate_filename(self, media_type: str):
        timestamp = datetime.now().strftime("%d%m%y_%H%M%S")
        extension = self.config.extensions.get(media_type, ".dat")
        return f"{timestamp}_{media_type}{extension}"

    @staticmethod
    def ensure_unique_file_name(folder: str, file_name: str) -> str:
        base_name, extension = os.path.splitext(file_name)
        counter = 1
        new_file_name = file_name

        while os.path.exists(os.path.join(folder, new_file_name)):
            new_file_name = f"{base_name}_{counter}{extension}"
            counter += 1

        return new_file_name

    async def save_file(self, file, folder: str, file_name: str):
        file_path = os.path.join(folder, file_name)
        await file.download_to_drive(file_path)
        self.logger.info(f"Saved file to {file_path}")
        return file_path
