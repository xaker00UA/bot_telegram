import os
from re import S
import re
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, FSInputFile
from aiogram.filters import Command
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


@insurance_router.message(Command("insurance_start"))
async def insurance_start(message: Message, state: FSMContext, locale):
    """
    Handler for the /insurance_start command.
    Sends a message indicating that the insurance process has started.
    """
    data = settings.get_localized_text(locale)["insurance"]
    await state.set_state(Insurance.photo_passport_front)

    await message.answer(data.get("start"))
    await message.answer_photo("https://surl.lu/czmaqw", caption="Id card front side ")


@insurance_router.message(Insurance.photo_passport_front, F.photo)
async def passport_front(message: Message, state: FSMContext, locale):
    url = await process_photo(message)
    await state.update_data(passport_front=url)
    await state.set_state(Insurance.photo_passport_back)
    data = settings.get_localized_text(locale)["insurance"]
    await message.answer(data.get("passport_back"))


@insurance_router.message(Insurance.photo_passport_back, F.photo)
async def passport_back(message: Message, state: FSMContext, locale):
    url = await process_photo(message)
    await state.update_data(passport_back=url)
    await state.set_state(Insurance.photo_tech_front)
    data = settings.get_localized_text(locale)["insurance"]
    await message.answer(data.get("technical_passport"))
    await message.answer_photo(
        "https://autoportal.ua/img/inf/novosti/prava_4_2.jpg",
        caption="Technical_passport_car",
    )


@insurance_router.message(Insurance.photo_tech_front, F.photo)
async def tech_front(message: Message, state: FSMContext, locale):
    url = await process_photo(message)
    await state.update_data(tech_front=url)
    await state.set_state(Insurance.photo_tech_back)
    data = settings.get_localized_text(locale)["insurance"]
    await message.answer(data.get("technical_passport_back"))


@insurance_router.message(Insurance.photo_tech_back, F.photo)
async def tech_back(message: Message, state: FSMContext, locale):
    url = await process_photo(message)
    await state.update_data(tech_back=url)
    text = settings.get_localized_text(locale)["insurance"]
    await message.answer("Processing documents...")

    data = await state.get_data()
    pdf_path = await generate_pdf_from_urls(
        [
            data["passport_front"],
            data["passport_back"],
            data["tech_front"],
            data["tech_back"],
        ]
    )
    res = await APIService().get_info(pdf_path)
    os.remove(pdf_path)
    inline_kb = get_confirm_keyboard("confirm_documents", "reject_documents")
    await state.set_data({"data": res})
    await message.answer(text.get("documents").format(**res), reply_markup=inline_kb)
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
    inst = inst.get("data")
    path = crate_temp_file(inst)

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
