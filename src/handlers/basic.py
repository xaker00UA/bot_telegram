from aiogram import types, Router
from aiogram.filters import CommandStart


from src.config.settings import settings
from src.keyboard.main import reply_kb

basic_router = Router()


@basic_router.message(CommandStart())
async def start_handler(message: types.Message, locale):
    data = settings.get_localized_text(locale)
    await message.answer(data.get("welcome"), reply_markup=reply_kb)
