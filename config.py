import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла (если есть)
load_dotenv()

# Токен бота (лучше хранить в переменных окружения)
BOT_TOKEN = os.getenv("BOT_TOKEN", "8001893279:AAFB4joHjTPSAoMdsniHPk5dM-ZM6uBqk1I")

# Пути к файлам
DATA_DIR = "data"
RESULTS_FILE = os.path.join(DATA_DIR, "survey_results.txt")

# Создаем папку data, если ее нет
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)