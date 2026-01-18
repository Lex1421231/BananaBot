import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler

# Импортируем конфигурацию
from config import BOT_TOKEN

# Импортируем обработчики
from handlers.start import start_command, help_command
from handlers.survey import (
    start_survey, process_age, process_gender, 
    process_activity, process_hobbies, confirm_survey, cancel_survey, skip_hobbies,
    AGE, GENDER, ACTIVITY, HOBBIES, CONFIRM
)
from handlers.common import show_statistics, unknown_command
from keyboards import get_start_keyboard

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Создаем ConversationHandler для опроса
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('survey', start_survey),
            MessageHandler(filters.Regex('^📋 Начать опрос$'), start_survey)
        ],
        states={
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_age)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_gender)],
            ACTIVITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_activity)],
            HOBBIES: [
                MessageHandler(filters.Regex('^✅ Готово$'), process_hobbies),
                MessageHandler(filters.Regex('^⏭️ Пропустить$'), skip_hobbies),
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_hobbies),
            ],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_survey)],
        },
        fallbacks=[
            CommandHandler('cancel', cancel_survey),
            CommandHandler('start', cancel_survey),
            MessageHandler(filters.Regex('^Отмена$'), cancel_survey)
        ],
        allow_reentry=True
    )
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(conv_handler)
    
    # Обработчик для кнопки статистики
    application.add_handler(
        MessageHandler(filters.Regex('^📊 Статистика$'), show_statistics)
    )
    
    # Обработчик для кнопки помощи
    application.add_handler(
        MessageHandler(filters.Regex('^ℹ️ Помощь$'), help_command)
    )
    
    # Обработчик неизвестных команд
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    
    # Стартовое сообщение
    application.add_handler(MessageHandler(filters.Regex('^/start$'), start_command))
    
    # Запускаем бота
    print("✅ Бот запущен! Нажмите Ctrl+C для остановки.")
    print("📊 Бот готов принимать опросы!")
    application.run_polling(allowed_updates=['message', 'callback_query'])

if __name__ == '__main__':
    main()