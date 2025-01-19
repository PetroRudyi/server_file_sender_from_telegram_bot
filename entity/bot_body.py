import logging
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

        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        self.application.add_handler(MessageHandler(filters.AUDIO, self.handle_audio))
        self.application.add_handler(MessageHandler(filters.VOICE, self.handle_voice))
        self.application.add_handler(MessageHandler(filters.VIDEO, self.handle_video))
        self.application.add_handler(MessageHandler(filters.ANIMATION, self.handle_animation))
        self.application.add_handler(MessageHandler(filters.Sticker.ALL, self.handle_sticker))
        self.application.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))


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

    def run(self):
        self.logger.info("Bot started. Running polling.")
        self.application.run_polling()
