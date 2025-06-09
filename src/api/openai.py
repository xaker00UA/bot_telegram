from src.config.settings import settings
from aiohttp import ClientSession


class APIOpenAI:
    """
    API client for OpenAI.
    """

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    async def _get(self, model: str, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }
        async with ClientSession() as client:
            async with client.post(
                self.base_url, json=payload, headers=headers
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data["choices"][0]["message"]["content"]

    async def generate_response(
        self, prompt: str, model: str = "qwen/qwen3-30b-a3b:free"
    ) -> str:
        return await self._get(model, prompt)
