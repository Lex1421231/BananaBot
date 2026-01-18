from telegram import Update
from telegram.ext import ContextTypes
from database import get_statistics

async def show_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает статистику опросов"""
    count = get_statistics()
    
    await update.message.reply_text(
        f"📊 Статистика опросов:\n\n"
        f"✅ Всего пройдено опросов: {count}\n"
        f"📁 Результаты сохраняются в файл: data/survey_results.txt"
    )

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик неизвестных команд"""
    await update.message.reply_text(
        "Неизвестная команда. Используйте /help для списка команд."
    )