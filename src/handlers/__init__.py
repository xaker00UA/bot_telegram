from aiogram import Router

# from src.handlers.basic import basic_router
from src.handlers.helpers import helper as helper_router
from src.handlers.insurance import insurance_router
from src.handlers.openai import openai_handler

__all__ = ("router",)


router = Router()

# router.include_router(basic_router)
router.include_router(helper_router)
router.include_router(insurance_router)
router.include_router(openai_handler)
