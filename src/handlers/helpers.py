from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.filters import Command

from src.config.settings import settings
from src.database.repo import set_user_language

helper = Router()


@helper.message(Command("get_language"))
async def get_language(message: Message, locale):
    """
    Handler for the /get_language command.
    Sends a message with the current language setting.
    """
    data = settings.get_localized_text(locale)["helpers"]
    await message.answer(data.get("current_language").format(locale=locale))


@helper.message(Command("set_language"))
async def get_language(message: Message, locale):

    data = settings.get_localized_text(locale)["helpers"]
    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="English", callback_data="en")],
            [InlineKeyboardButton(text="Русский", callback_data="ru")],
            [InlineKeyboardButton(text="Українська", callback_data="ua")],
        ]
    )
    await message.answer(data.get("change_language"), reply_markup=inline_kb)


@helper.callback_query(F.data.in_(["en", "ru", "ua"]))
async def set_language_callback(callback: CallbackQuery, locale):
    lang_code = callback.data
    user_id = callback.from_user.id
    data = settings.get_localized_text(locale)["helpers"]
    # Сохраняем язык
    set_user_language(user_id, lang_code)

    # Отвечаем пользователю
    message_text = data.get("set_language").format(locale=lang_code)
    await callback.answer()
    await callback.message.answer(message_text)