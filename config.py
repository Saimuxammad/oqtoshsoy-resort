import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()


class Config:
    # Основные настройки
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-please-change'

    # Telegram настройки
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

    # Настройки приложения
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    # Языковые настройки
    LANGUAGES = ['uz', 'ru']
    DEFAULT_LANGUAGE = 'ru'