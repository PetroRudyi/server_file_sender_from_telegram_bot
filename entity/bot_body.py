import logging
import os
import pandas as pd
from datetime import datetime
from datetime import time, timezone, timedelta

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from config import Config
from entity.filemanager import FileManager

class LoaderBot:
    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.file_manager = FileManager(config, logger)
        self.application = ApplicationBuilder().token(config.bot_token).build()

        self.white_user_filter = filters.User(user_id=config.white_users_list)

        self.application.job_queue.start()
        self.application.add_handler(CommandHandler("start", self.start, filters=self.white_user_filter))
        self.application.add_handler(MessageHandler(self.white_user_filter & filters.PHOTO, self.handle_photo))
        self.application.add_handler(MessageHandler(self.white_user_filter & filters.AUDIO, self.handle_audio))
        self.application.add_handler(MessageHandler(self.white_user_filter & filters.VOICE, self.handle_voice))
        self.application.add_handler(MessageHandler(self.white_user_filter & filters.VIDEO, self.handle_video))
        self.application.add_handler(MessageHandler(self.white_user_filter & filters.ANIMATION, self.handle_animation))
        self.application.add_handler(MessageHandler(self.white_user_filter & filters.Sticker.ALL, self.handle_sticker))
        self.application.add_handler(MessageHandler(self.white_user_filter & filters.Document.ALL, self.handle_document))

        self.application.add_handler(CommandHandler("feed", self.handle_event, filters=self.white_user_filter))
        self.application.add_handler(CommandHandler("sleep", self.handle_event, filters=self.white_user_filter))
        self.application.add_handler(CommandHandler("play", self.handle_event, filters=self.white_user_filter))
        self.application.add_handler(CommandHandler("pepe", self.handle_event, filters=self.white_user_filter))
        self.application.add_handler(CommandHandler("shit", self.handle_event, filters=self.white_user_filter))


        self.schedule_daily_report()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Hello! Send me any media, and I'll save it.")
        self.logger.info("Started bot for user %s", update.message.from_user.id)

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        file_id = update.message.photo[-1].file_id
        media_type = "photo"
        await self.process_media(file_id, media_type, None, context)

    async def handle_audio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        file_id = update.message.audio.file_id
        file_name = update.message.audio.file_name
        media_type = "audio"
        await self.process_media(file_id, media_type, file_name, context)

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        file_id = update.message.voice.file_id
        media_type = "voice"
        await self.process_media(file_id, media_type, None, context)

    async def handle_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        file_id = update.message.video.file_id
        file_name = update.message.video.file_name
        media_type = "video"
        await self.process_media(file_id, media_type, file_name, context)

    async def handle_sticker(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        file_id = update.message.sticker.file_id
        media_type = "sticker"
        await self.process_media(file_id, media_type, None, context)

    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        file_id = update.message.document.file_id
        file_name = update.message.document.file_name
        media_type = "document"

        if hasattr(update.message.document, 'mime_type') and "image" in update.message.document.mime_type:
            media_type = "doc_photo"
        elif update.message.document.file_name and update.message.document.file_name.endswith(".torrent"):
            media_type = "torrent"

        await self.process_media(file_id, media_type, file_name, context)

    @staticmethod
    async def handle_animation(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Currently, saving GIFs is not supported.")

    async def process_media(self, file_id, media_type, file_name, context):
        folder = self.file_manager.get_folder_for_media(media_type)

        if not file_name:
            file_name = self.file_manager.generate_filename(media_type)

        file_name = self.file_manager.ensure_unique_file_name(folder, file_name)

        file = await context.bot.get_file(file_id)
        await self.file_manager.save_file(file, folder, file_name)

        await context.bot.send_message(chat_id=context._chat_id, text=f"Your {media_type} has been saved.")

    async def handle_event(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message_text = update.message.text
        command, *details = message_text.split(" ", 1)

        if not details:
            await update.message.reply_text("Формат: /feed опис події")
            return

        event_type = command.lstrip('/')
        note = details[0].strip()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        file_path_saving = self.config.directories.get('sirko_logs', os.path.join(self.config.storage_directory, "others"))
        file_path = os.path.join(file_path_saving, 'sirko_logs.csv')
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
        else:
            df = pd.DataFrame(columns=["date", "situation_type", "note"])

        print(file_path)

        new_entry = pd.DataFrame([[timestamp, event_type, note]], columns=["date", "situation_type", "note"])
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv(file_path, index=False)

        await update.message.reply_text(f"Запис збережено: {event_type} - {note}")
        self.logger.info("Збережено запис: %s, %s", event_type, note)

    def schedule_daily_report(self):

        file_path_saving = self.config.directories.get('sirko_logs',
                                                       os.path.join(self.config.storage_directory, "others"))
        file_path = os.path.join(file_path_saving, 'sirko_logs.csv')

        async def send_csv(context: ContextTypes.DEFAULT_TYPE):

            print('start sending csv')
            chat_id = context.job.chat_id
            if os.path.exists(file_path):
                await context.bot.send_document(chat_id, document=open(file_path, "rb"))
            else:
                await context.bot.send_message(chat_id, "Файл подій відсутній.")

        self.application.job_queue.run_daily(send_csv,
                                             time(hour=0, minute=0, second=0, tzinfo=timezone(timedelta(hours=2))),
                                             chat_id=216757486)
        self.application.job_queue.start()
    def run(self):
        self.logger.info("Bot started. Running polling.")
        self.application.run_polling()
