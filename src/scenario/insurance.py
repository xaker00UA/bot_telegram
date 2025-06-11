from aiogram.fsm.state import StatesGroup, State


class Insurance(StatesGroup):
    photo_passport_front = State()
    photo_tech_front = State()
    confirm_documents = State()
    confirm_price = State()
