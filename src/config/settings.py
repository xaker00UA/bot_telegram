import json
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    TOKEN: str
    FILE_TEXT: str = "message"
    API_KEY: str
    OPENAI_API_KEY: str
    ADMIN_ID: int

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    def get_localized_text(self, local: str = "en") -> dict:
        """Возвращает содержимое файла локализации в виде словаря."""
        path = Path(f"src/locales/{self.FILE_TEXT}_{local}.json")
        if path.exists():
            with path.open("r", encoding="utf-8") as file:
                return json.load(file)
        else:
            with open(
                f"src/locales/{self.FILE_TEXT}_en.json", "r", encoding="utf-8"
            ) as file:
                return json.load(file)


settings = Settings()
