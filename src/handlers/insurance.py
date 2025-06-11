from multiprocessing.spawn import import_main_path
from operator import add
import os
from re import S
import re
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, FSInputFile
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from src.service.generated_doc import crate_temp_file, generate_pdf_from_urls
from src.api.minde import APIService
from src.keyboard.main import get_confirm_keyboard
from src.config.settings import settings
from src.scenario.insurance import Insurance


insurance_router = Router()


async def process_photo(message: Message):
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    return f"https://api.telegram.org/file/bot{message.bot.token}/{file.file_path}"


@insurance_router.message(CommandStart())
async def insurance_start(message: Message, state: FSMContext, locale):
    """
    Handler for the /insurance_start command.
    Sends a message indicating that the insurance process has started.
    """
    data = settings.get_localized_text(locale)
    await message.answer(text=data.get("welcome"))
    await state.set_state(Insurance.photo_passport_front)
    await message.answer(text=data.get("insurance").get("start"))


@insurance_router.message(Insurance.photo_passport_front, F.photo)
async def passport_front(message: Message, state: FSMContext, locale):
    url = await process_photo(message)
    await state.set_state(Insurance.photo_tech_front)
    data = settings.get_localized_text(locale)["insurance"]
    await message.answer(text="Processing documents...")
    res = await APIService().get_info_pass(url)
    await state.set_data({"passport": res})
    await message.answer(text=data.get("technical_passport"))


@insurance_router.message(Insurance.photo_tech_front, F.photo)
async def tech_front(message: Message, state: FSMContext, locale):
    url = await process_photo(message)
    await message.answer("Processing documents...")
    res = await APIService().get_info_tech(url)
    await state.update_data(tech=res)
    data = await state.get_data()
    text = settings.get_localized_text(locale)["insurance"]
    inline_kb = get_confirm_keyboard("confirm_documents", "reject_documents")
    await message.answer(
        text=text.get("documents").format(**data["tech"], **data["passport"]),
        reply_markup=inline_kb,
    )
    await state.set_state(Insurance.confirm_documents)


@insurance_router.callback_query(
    Insurance.confirm_documents, F.data == "confirm_documents"
)
async def confirm_documents(
    callback: CallbackQuery, state: FSMContext, locale, **kwargs
):
    """
    Handler for confirming documents.
    Sends a message indicating that the documents have been confirmed.
    """
    await callback.answer()
    await state.set_state(Insurance.confirm_price)
    data = settings.get_localized_text(locale)["insurance"]
    inline_kb = get_confirm_keyboard("confirm_price", "reject_price")
    await callback.message.answer(data.get("confirm_documents"), reply_markup=inline_kb)


@insurance_router.callback_query(
    Insurance.confirm_documents, F.data == "reject_documents"
)
async def reject_documents(
    callback: CallbackQuery, state: FSMContext, locale, **kwargs
):
    """
    Handler for rejecting documents.
    Sends a message indicating that the documents have been rejected.
    """
    await callback.answer()
    await state.set_state(Insurance.photo_passport_front)
    data = settings.get_localized_text(locale)["insurance"]
    await callback.message.answer(data.get("reject_documents"))


@insurance_router.callback_query(Insurance.confirm_price, F.data == "confirm_price")
async def confirm_price(callback: CallbackQuery, state: FSMContext, locale, **kwargs):
    """
    Handler for confirming the price.
    Sends a message indicating that the price has been confirmed.
    """
    data = settings.get_localized_text(locale)["insurance"]
    await callback.answer(data.get("confirm_price"))
    inst = await state.get_data()
    result = inst.get("tech") | inst.get("passport")
    path = crate_temp_file(result)

    await callback.bot.send_document(
        callback.from_user.id,
        document=FSInputFile(path),
        caption=data.get("insurance"),
    )

    await state.clear()


@insurance_router.callback_query(Insurance.confirm_price, F.data == "reject_price")
async def reject_price(callback: CallbackQuery, state: FSMContext, locale, **kwargs):
    """
    Handler for rejecting the price.
    Sends a message indicating that the price has been rejected.
    """
    data = settings.get_localized_text(locale)["insurance"]
    inline_kb = get_confirm_keyboard("confirm_price", "reject_price")
    await callback.answer()
    await callback.message.answer(data.get("reject_price"), reply_markup=inline_kb)
