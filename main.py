import logging
from config import Config
from entity.bot_body import LoaderBot

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    config = Config()
    bot = LoaderBot(config, logger)
    bot.run()

