from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

kb = [[KeyboardButton(text="/insurance_start")]]
reply_kb = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def get_confirm_keyboard(yes_callback: str, no_callback: str) -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Confirm", callback_data=yes_callback),
                InlineKeyboardButton(text="❌ Cancel", callback_data=no_callback),
            ]
        ]
    )
