from aiogram import types, Router


from src.api.openai import APIOpenAI

openai_handler = Router()


@openai_handler.message()
async def handle_openai_message(message: types.Message, **kwargs):
    msg = await message.answer("Generating response, please wait...")
    text = await APIOpenAI().generate_response(message.text)
    if not text:
        text = "No response generated."
    if len(text) > 4000:
        for i in range(0, len(text), 4000):
            await msg.answer(text[i : i + 4000])
    else:
        await msg.answer(text)
