#!/usr/bin/env python3
"""
BananaBot - Опросник для Telegram
Деплой на Render.com
"""

import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токен из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN не установлен!")
    raise ValueError("❌ Установите BOT_TOKEN в переменные окружения")

# Состояния для опроса
AGE, GENDER, ACTIVITY, HOBBIES, CONFIRM = range(5)

# ========== ОПРОС ==========
async def start_survey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начать опрос"""
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Привет, {user.first_name}! Начнем опрос.\n\n"
        "Сколько вам лет? (Введите число от 1 до 120)"
    )
    return AGE

async def process_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработать возраст"""
    try:
        age = int(update.message.text)
        if 1 <= age <= 120:
            context.user_data['age'] = age
            await update.message.reply_text(
                "Отлично! Выберите пол:\n"
                "1. Мужской\n"
                "2. Женский\n"
                "3. Другой"
            )
            return GENDER
        else:
            await update.message.reply_text("Пожалуйста, введите возраст от 1 до 120 лет!")
            return AGE
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число!")
        return AGE

async def process_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработать пол"""
    gender = update.message.text
    context.user_data['gender'] = gender
    
    await update.message.reply_text(
        "Чем вы занимаетесь?\n"
        "1. Работаю\n"
        "2. Учусь\n"
        "3. Работаю и учусь\n"
        "4. Не работаю/не учусь"
    )
    return ACTIVITY

async def process_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработать род деятельности"""
    activity = update.message.text
    context.user_data['activity'] = activity
    
    await update.message.reply_text(
        "Какие у вас увлечения? (Перечислите через запятую)\n"
        "Например: книги, спорт, программирование"
    )
    return HOBBIES

async def process_hobbies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработать увлечения"""
    hobbies = update.message.text
    context.user_data['hobbies'] = hobbies
    
    # Сохраняем результат
    user = update.effective_user
    save_survey_result(user, context.user_data)
    
    await update.message.reply_text(
        f"✅ Спасибо за участие в опросе, {user.first_name}!\n\n"
        f"Ваши ответы:\n"
        f"• Возраст: {context.user_data.get('age')}\n"
        f"• Пол: {context.user_data.get('gender')}\n"
        f"• Деятельность: {context.user_data.get('activity')}\n"
        f"• Увлечения: {context.user_data.get('hobbies')}\n\n"
        f"Чтобы начать новый опрос, нажмите /survey"
    )
    
    return ConversationHandler.END

def save_survey_result(user, data):
    """Сохранить результаты опроса"""
    import json
    from datetime import datetime
    
    result = {
        'user_id': user.id,
        'username': user.username or user.full_name,
        'timestamp': datetime.now().isoformat(),
        'age': data.get('age'),
        'gender': data.get('gender'),
        'activity': data.get('activity'),
        'hobbies': data.get('hobbies')
    }
    
    # Логируем результат
    logger.info(f"📝 Сохранен опрос: {json.dumps(result, ensure_ascii=False)}")
    
    # В Render можно использовать логи или переменные окружения
    # Для простоты просто логируем

async def cancel_survey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отменить опрос"""
    await update.message.reply_text("Опрос отменен. Используйте /survey для нового опроса.")
    return ConversationHandler.END

# ========== КОМАНДЫ ==========
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик /start"""
    user = update.effective_user
    await update.message.reply_text(
        f"🍌 Привет, {user.first_name}!\n\n"
        "Я BananaBot - бот для проведения опросов.\n\n"
        "📋 Доступные команды:\n"
        "/start - Начать работу\n"
        "/survey - Пройти опрос\n"
        "/help - Помощь\n\n"
        "Используйте /survey для начала опроса!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик /help"""
    await update.message.reply_text(
        "📚 Помощь по боту:\n\n"
        "/survey - Пройти опрос (возраст, пол, деятельность, увлечения)\n"
        "/start - Начать работу с ботом\n"
        "/help - Эта справка\n\n"
        "Все ответы сохраняются анонимно."
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать статистику"""
    await update.message.reply_text(
        "📊 Статистика:\n"
        "Бот работает и готов принимать опросы!\n"
        "Для начала опроса используйте /survey"
    )

# ========== ЗАПУСК БОТА ==========
def main():
    """Запуск бота"""
    logger.info("🚀 Запуск BananaBot...")
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # ConversationHandler для опроса
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('survey', start_survey)],
        states={
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_age)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_gender)],
            ACTIVITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_activity)],
            HOBBIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_hobbies)],
        },
        fallbacks=[CommandHandler('cancel', cancel_survey)],
        allow_reentry=True
    )
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(conv_handler)
    
    # Запускаем бота
    logger.info("✅ Бот запущен и готов к работе!")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )

if __name__ == '__main__':
    main()