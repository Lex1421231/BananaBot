import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Токен бота из переменных окружения (обязательно!)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Проверяем, что токен есть
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не установлен! Добавьте его в переменные окружения.")

# Пути к файлам
DATA_DIR = "data"
RESULTS_FILE = os.path.join(DATA_DIR, "survey_results.txt")

# Создаем папку data, если ее нет
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Настройки для вебхука (если нужно)
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
PORT = int(os.getenv("PORT", 10000))