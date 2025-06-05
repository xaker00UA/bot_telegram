import datetime
import random
import aiohttp
from PIL import Image
from io import BytesIO
import uuid
import os


async def generate_pdf_from_urls(urls: list[str]) -> str:
    """
    Скачивает изображения по URL, объединяет их в PDF и сохраняет во временный файл.

    :param urls: Список URL изображений
    :return: Путь к PDF-файлу
    """
    images = []
    output_dir = "output"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    async with aiohttp.ClientSession() as session:
        for url in urls:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise Exception(
                        f"Ошибка загрузки изображения: {url} — {resp.status}"
                    )
                img_bytes = await resp.read()
                img = Image.open(BytesIO(img_bytes)).convert("RGB")
                images.append(img)

    if not images:
        raise Exception("Не удалось загрузить ни одного изображения")

    output_path = os.path.join(output_dir, f"insurance_{uuid.uuid4().hex}.pdf")
    images[0].save(output_path, save_all=True, append_images=images[1:])
    return output_path


def crate_temp_file(data: dict) -> str:
    """
    Создает временный файл с заданным содержимым и расширением.

    :param content: Содержимое файла в виде байтов
    :param extension: Расширение файла (по умолчанию 'pdf')
    :return: Путь к созданному временно файлу
    """
    template_path = os.path.join("tmp", "insurance_template.txt")
    data.update(
        {
            "policy_number": f"{random.randint(0, 999999999):09}",
            "start_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "end_date": (
                datetime.datetime.now() + datetime.timedelta(days=365)
            ).strftime("%Y-%m-%d"),
            "issue_date": datetime.datetime.now().strftime("%Y-%m-%d"),
        }
    )
    # Чтение шаблона
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    # Заполнение шаблона
    output = template
    for key, value in data.items():
        output = output.replace(f"{{{{ {key} }}}}", str(value))

    # Создание директории для результата
    output_dir = "document"
    os.makedirs(output_dir, exist_ok=True)

    first_name = data.get("first_name")
    last_name = data.get("last_name")

    filename = f"{first_name}_{last_name}_{uuid.uuid4().hex}.txt"
    output_path = os.path.join(output_dir, filename)

    # Сохранение файла
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output)
    return output_path
