import os
from dataclasses import dataclass, field
from zoneinfo import ZoneInfo

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str = field(repr=False)
    allowed_user_id: int
    timezone: ZoneInfo


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        telegram_bot_token=os.environ["TELEGRAM_BOT_TOKEN"],
        allowed_user_id=int(os.environ["ALLOWED_USER_ID"]),
        timezone=ZoneInfo(os.environ["TIMEZONE"]),
    )
