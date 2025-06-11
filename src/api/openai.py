import tiktoken
from aiohttp import ClientSession
from src.config.settings import settings
from src.database.repo import get_messages, add_message


class APIOpenAI:
    """
    API client for OpenAI.
    """

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    async def _get(self, model: str, prompt: list[dict]) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": prompt,
            "max_tokens": 700,
        }
        async with ClientSession() as client:
            async with client.post(
                self.base_url, json=payload, headers=headers
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data["choices"][0]["message"]["content"]

    def _get_count_tokens(self, messages: list[dict], model: str) -> int:
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")

        tokens_per_message = 3
        tokens_per_name = 1

        total_tokens = 0
        for message in messages:
            total_tokens += tokens_per_message
            for key, value in message.items():
                total_tokens += len(encoding.encode(value))
                if key == "name":
                    total_tokens += tokens_per_name
        total_tokens += 3
        return total_tokens

    def trim_messages_to_fit(
        self, messages, model, max_tokens=40960, response_tokens=700
    ):
        messages.insert(
            0,
            {
                "role": "system",
                "content": "Ты страховой помощник, помоги оформить страховку шаг за шагом. Ты должен запросить у пользователя фото паспорта и фото доукмента подтверждающий идентификацию вашего автомобиля",
            },
        )
        while self._get_count_tokens(messages, model) + response_tokens > max_tokens:
            if len(messages) <= 1:
                break
            messages.pop(0)
        return messages

    async def generate_response(
        self, prompt: str, id_user: int, model: str = "qwen/qwen3-30b-a3b:free"
    ) -> str:
        data = get_messages(user_id=id_user)
        data = [message.shema() for message in data]
        data = self.trim_messages_to_fit(data, model)
        response = await self._get(model, data)
        return response
