import logging
from datetime import datetime

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from personal_assistant.config import Settings, load_settings

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reply to /start and show the user's Telegram ID"""
    user = update.effective_user
    await update.message.reply_text(
        f"Hi {user.first_name}! Your Telegram user ID is {user.id}."
    )


async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reply to /time with the current time in the user's timezone."""
    settings: Settings = context.bot_data["settings"]
    now = datetime.now(settings.timezone)
    formatted = now.strftime("%d.%m.%Y %H:%M")
    await update.message.reply_text(f"Time is: {formatted}")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the user's message back to them."""
    logger.info("Message from %s: %s", update.effective_user.id, update.message.text)
    await update.message.reply_text(update.message.text)


def main() -> None:
    settings = load_settings()

    app = Application.builder().token(settings.telegram_bot_token).build()
    app.bot_data["settings"] = settings
    allowed = filters.User(user_id=settings.allowed_user_id)

    app.add_handler(CommandHandler("start", start, filters=allowed))
    app.add_handler(CommandHandler("time", time_command, filters=allowed))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & allowed, echo))

    logger.info("Bot is running. Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
