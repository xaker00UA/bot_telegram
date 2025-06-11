import asyncio
from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.base import DefaultKeyBuilder

from src.handlers import router
from src.config.settings import settings
from src.middleware.middleware import (
    GlobalExceptionMiddleware,
    LocalizationMiddleware,
    AddContextMessageMiddleware,
)

storage = RedisStorage.from_url(
    "redis://localhost:6379/4",  # или конфигурация твоего Redis
    key_builder=DefaultKeyBuilder(prefix="fsm"),  # необязательно, но хорошо
)


async def set_commands(bot: Bot):
    data = settings.get_localized_text()["description_command"]
    commands = [
        BotCommand(command="start", description=data["init"]),
        BotCommand(command="get_language", description=data["get_language"]),
        BotCommand(command="set_language", description=data["set_language"]),
        # BotCommand(command="insurance_start", description=data["insurance_start"]),
    ]
    await bot.set_my_commands(commands)


async def main():
    bot = Bot(token=settings.TOKEN)
    logger.info("Bot initialized")
    await set_commands(bot)
    dp = Dispatcher()
    dp.message.middleware.register(LocalizationMiddleware())
    dp.callback_query.middleware.register(LocalizationMiddleware())
    dp.message.middleware.register(GlobalExceptionMiddleware(bot))
    dp.callback_query.middleware.register(GlobalExceptionMiddleware(bot))
    dp.message.middleware.register(AddContextMessageMiddleware())
    dp.include_router(router)
    logger.info("Starting bot")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    logger.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
