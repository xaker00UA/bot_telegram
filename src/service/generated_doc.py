import datetime
import random
import uuid
import os


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

    first_name = data.get("surnames")
    last_name = data.get("given_names")

    filename = f"{first_name}_{last_name}_{uuid.uuid4().hex}.txt"
    output_path = os.path.join(output_dir, filename)

    # Сохранение файла
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output)
    return output_path
