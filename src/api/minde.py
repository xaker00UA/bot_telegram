import asyncio
from loguru import logger
from aiohttp import ClientSession, FormData

from src.err.exceptions import DocumentProcessingError, DocumentProcessingTime
from src.config.settings import settings


class APIService:

    async def _post(self, url, document):
        async with ClientSession(
            headers={"Authorization": settings.API_KEY}
        ) as session:
            form = FormData()

            form.add_field("document", document)

            async with session.post(url, data=form) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def _get(self, url):
        async with ClientSession(
            headers={"Authorization": settings.API_KEY},
        ) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()

    async def get_info_document(
        self, url, file_url: str, timeout: int = 30, poll_interval: int = 2
    ):
        """
        Получает данные паспорта через сторонний API Mindee.
        :param file_url: URL файла для обработки
        :param timeout: максимальное время ожидания (сек)
        :param poll_interval: интервал опроса статуса (сек)
        :return: данные документа
        :raises ValueError: если обработка не завершена за timeout
        """

        response = await self._post(url, file_url)
        job_url = response.get("job", {}).get("polling_url")
        if not job_url:
            logger.error("Не удалось получить polling_url от Mindee API.")
            raise ValueError("Не удалось получить polling_url от Mindee API.")
        elapsed = 0
        while elapsed < timeout:
            document = await self._get(job_url)
            status = document.get("job", {}).get("status")
            if status == "completed":
                return document.get("document")
            elif status == "failed":
                logger.info("Обработка документа не удалась.")
                raise DocumentProcessingError("Обработка документа не удалась.")
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
        logger.error("Обработка документа заняла слишком много времени.")
        raise DocumentProcessingTime(
            "Обработка документа заняла слишком много времени."
        )

    async def get_info_pass(self, file_path):
        url = "https://api.mindee.net/v1/products/mindee/international_id/v2/predict_async"
        response = await self.get_info_document(url, file_path)
        data = response.get("inference", {}).get("prediction", {})
        result = {}
        for key, value in data.items():
            if isinstance(value, dict):
                result[key] = value.get("value") if value.get("value") else None
            if isinstance(value, list):
                result[key] = ", ".join(i.get("value") for i in value if i.get("value"))
        return result

    async def get_info_tech(self, file_path):
        url = "https://api.mindee.net/v1/products/xaker/vehicle_dentification_document/v1/predict_async"
        response = await self.get_info_document(url, file_path)
        data = response.get("inference", {}).get("prediction", {})
        result = {}
        for key, value in data.items():
            result[key] = value.get("value") if value.get("value") else None
        return result
