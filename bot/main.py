"""Main bot file"""
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from .database.db import init_db, close_db
from .database import async_session_maker
from .questions.loader import QuestionLoader
from .handlers import start, quiz, stats

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def load_questions_to_db():
    """Load all questions into database"""
    async with async_session_maker() as session:
        loader = QuestionLoader()
        total = await loader.load_all_questions(session)
        logger.info(f"Loaded {total} questions into database")


async def main():
    """Main bot function"""
    # Get bot token
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError("BOT_TOKEN not found in environment variables")

    # Initialize bot and dispatcher
    bot = Bot(token=bot_token)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Register routers
    dp.include_router(start.router)
    dp.include_router(quiz.router)
    dp.include_router(stats.router)

    # Initialize database
    logger.info("Initializing database...")
    await init_db()

    # Load questions
    logger.info("Loading questions into database...")
    await load_questions_to_db()

    # Start polling
    logger.info("Bot started!")
    try:
        await dp.start_polling(bot)
    finally:
        await close_db()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
