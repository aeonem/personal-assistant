import logging
import sqlite3
from datetime import datetime
from pathlib import Path

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from personal_assistant.config import Settings, load_settings
from personal_assistant.task_text import format_task_line, parse_add_args
from personal_assistant.tasks import add_task, complete_task, connect, list_open_tasks

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


ADD_USAGE = "Usage: /add 2026-11-06 15:00 Dentist  or  /add Pay the bill"


async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a task: /add [YYYY-MM-DD HH:MM] title"""
    settings: Settings = context.bot_data["settings"]
    db: sqlite3.Connection = context.bot_data["db"]

    try:
        title, due_at = parse_add_args(context.args, settings.timezone)
    except ValueError:
        await update.message.reply_text(ADD_USAGE)
        return

    task_id = add_task(db, title, due_at)
    await update.message.reply_text(f"Added task #{task_id}: {title}")


DONE_USAGE = "Usage: /done 3"


async def done_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Complete a task: /done <task id>"""
    db: sqlite3.Connection = context.bot_data["db"]

    try:
        task_id = int(context.args[0])
    except (ValueError, IndexError):
        await update.message.reply_text(DONE_USAGE)
        return

    completed = complete_task(db, task_id)

    if completed:
        await update.message.reply_text(f"Done task #{task_id}")
    else:
        await update.message.reply_text(f"No open task #{task_id}.")


async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all open tasks."""
    settings: Settings = context.bot_data["settings"]
    db: sqlite3.Connection = context.bot_data["db"]

    tasks = list_open_tasks(db)
    if not tasks:
        await update.message.reply_text("No open tasks!!! :)")
        return

    lines = [format_task_line(task, settings.timezone) for task in tasks]
    await update.message.reply_text("\n".join(lines))


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the user's message back to them."""
    logger.info("Message from %s: %s", update.effective_user.id, update.message.text)
    await update.message.reply_text(update.message.text)


def main() -> None:
    settings = load_settings()

    Path(settings.database_path).parent.mkdir(parents=True, exist_ok=True)
    db = connect(settings.database_path)

    app = Application.builder().token(settings.telegram_bot_token).build()
    app.bot_data["settings"] = settings
    app.bot_data["db"] = db
    allowed = filters.User(user_id=settings.allowed_user_id)

    app.add_handler(CommandHandler("start", start, filters=allowed))
    app.add_handler(CommandHandler("time", time_command, filters=allowed))
    app.add_handler(CommandHandler("add", add_command, filters=allowed))
    app.add_handler(CommandHandler("list", list_command, filters=allowed))
    app.add_handler(CommandHandler("done", done_command, filters=allowed))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & allowed, echo))

    logger.info("Bot is running. Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
