from aiogram import types, Router


from src.api.openai import APIOpenAI

openai_handler = Router()


@openai_handler.message()
async def handle_openai_message(message: types.Message, **kwargs):
    msg = await message.answer("Generating response, please wait...")
    text = await APIOpenAI().generate_response(message.text)
    print(text)
    if not text:
        text = "No response generated."
    await msg.edit_text(text)
