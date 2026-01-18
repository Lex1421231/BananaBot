from telegram import Update
from telegram.ext import ContextTypes
from keyboards import get_start_keyboard

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    welcome_text = """
👋 Привет! Я бот для проведения опроса.

С помощью этого бота вы можете принять участие в опросе на следующие темы:
• Возраст
• Пол
• Род деятельности (работа/учеба)
• Увлечения и хобби

📊 Все ответы сохраняются анонимно.

Нажмите "📋 Начать опрос" для участия!
    """
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_start_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
📚 Доступные команды:

/start - Начало работы с ботом
/help - Показать это сообщение
/cancel - Отменить текущий опрос
/survey - Начать новый опрос

Или используйте кнопки меню!
    """
    await update.message.reply_text(help_text)