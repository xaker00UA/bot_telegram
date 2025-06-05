from aiogram.fsm.state import StatesGroup, State


class Insurance(StatesGroup):
    photo_passport_front = State()
    photo_passport_back = State()
    photo_tech_front = State()
    photo_tech_back = State()
    confirm_documents = State()
    confirm_price = State()
