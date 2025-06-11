from functools import wraps
from operator import add
from aiogram import BaseMiddleware, Bot
from aiogram.types import Message
from typing import Awaitable, Callable, Dict, Any
from aiogram.types import TelegramObject
from loguru import logger


from src.config.settings import settings
from src.err.exceptions import BaseCustomException
from src.database.repo import get_user_language, add_message


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


class AddContextMessageMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            user_id = event.from_user.id
            text = event.text or event.caption or ""

            # Сохраняем сообщение пользователя
            add_message(user_id, text, is_ai=False)

            # Сохраняем оригинальную функцию answer
            original_answer = event.answer

            async def custom_answer(*args, **kwargs):
                # Вызов оригинального метода
                sent_message = await original_answer(*args, **kwargs)

                # Получаем текст, который бот отправил
                response_text = kwargs.get("text") or (args[0] if args else "")

                # Сохраняем ответ бота
                if response_text and response_text not in [
                    "Generating response, please wait...",
                    "No response generated.",
                ]:
                    add_message(user_id, response_text, is_ai=True)

                return sent_message

            # Подменяем метод answer
            object.__setattr__(event, "answer", custom_answer)

            # Продолжаем цепочку
            return await handler(event, data)
