# config.py
import os
from typing import Optional
# Импортируем BaseSettings из pydantic_settings (для Pydantic v2)
# Если используете Pydantic v1, импортируйте из pydantic
from pydantic_settings import BaseSettings
# from pydantic import BaseSettings # Для Pydantic v1

# Загружаем переменные окружения из .env файла
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    # --- API Configuration ---
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_URL: str = "https://openrouter.ai/api/v1"
    AI_MODEL: str = "deepseek/deepseek-chat"

    # --- Wappi Configuration ---
    WAPPI_API_URL: Optional[str] = None
    WAPPI_TOKEN: Optional[str] = None
    WAPPI_PROFILE_ID: Optional[str] = None

    # --- Database Configuration ---
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"

    # --- Bot Configuration ---
    ASSISTANT_NAME: str = "Менеджер"

    # --- Price Configuration (Example for РФ) ---
    # Обратите внимание: используем property или метод для сложных структур,
    # или определяем их напрямую как словарь.
    # Pydantic может валидировать словари, но не всегда удобно.
    # Для простоты оставим как словарь, но помним об этом.
    PRICES: dict = {
        "digital": {
            "30x40": 2850,
            "40x60": 4190,
            "50x70": 5390,
            "60x80": 6550,
            "70x100": 8450,
            "80x120": 10350,
        },
        "acrylic": {
            "30x40": 12800,
            "40x60": 14500,
            "50x70": 16800,
            "60x80": 18100,
            "70x100": 19500,
            "80x120": 22000,
        },
        "oil": {
            "40x60": 24800,
            "50x70": 28900,
            "60x80": 36700,
            "70x100": 47500,
            "80x120": 63900,
        },
        "additional_person": {
            "digital": 650,
            "acrylic": 2000,
            "oil": 3000,
        },
        "acrylic_background": 4290,
        "oil_background": 12770,
        "premium_canvas": {
            "40x60": 1000,
            "50x70": 1100,
            "60x80": 1100,
            "70x100": 1300,
            "80x120": 1500,
        }
    }

    class Config:
        # Указываем файл .env для загрузки переменных
        env_file = ".env"
        # (Опционально) Указываем кодировку, если в .env есть не-ASCII символы
        # env_file_encoding = 'utf-8'

# Создаем экземпляр настроек
settings = Settings()

# --- (Альтернатива, если не используем BaseSettings напрямую для PRICES) ---
# Можно определить PRICES как константу вне класса, если есть сложности с валидацией
# PRICES = settings.PRICES # Или просто используем settings.PRICES напрямую
