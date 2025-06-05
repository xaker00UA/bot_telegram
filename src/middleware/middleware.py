from aiogram import BaseMiddleware, Bot
from typing import Callable, Dict, Any
from aiogram.types import TelegramObject
from loguru import logger


from src.config.settings import settings
from src.err.exceptions import BaseCustomException
from src.database.repo import get_user_language


class LocalizationMiddleware(BaseMiddleware):
    async def __call__(
        self, handler: Callable, event: TelegramObject, data: Dict[str, Any]
    ) -> Any:
        user_lang = get_user_language(event.from_user.id)
        data["locale"] = user_lang
        return await handler(event, data)


class GlobalExceptionMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot

    async def __call__(self, handler, event, data):
        try:
            return await handler(event, data)
        except BaseCustomException as e:
            logger.error(str(e))
            if hasattr(event, "answer"):
                await event.answer(str(e))
        except Exception as e:
            logger.exception(str(e))
            await self.bot.send_message(settings.ADMIN_ID, str(e))
            if hasattr(event, "answer"):
                await event.answer("Try again later")

        return True
