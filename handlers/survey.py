from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from keyboards import get_gender_keyboard, get_activity_keyboard, get_hobbies_keyboard, get_confirm_keyboard
from database import save_survey_result
import re

# Состояния для ConversationHandler
AGE, GENDER, ACTIVITY, HOBBIES, CONFIRM = range(5)

async def start_survey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало опроса"""
    # Инициализируем данные пользователя
    user = update.effective_user
    context.user_data['survey'] = {
        'user_id': user.id,
        'username': user.username or user.full_name,
        'hobbies': []  # список для увлечений
    }
    
    await update.message.reply_text(
        "📝 Отлично! Начнем опрос.\n\n"
        "Сколько вам лет? (Введите число от 1 до 120)"
    )
    
    return AGE

async def process_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка возраста"""
    age_text = update.message.text.strip()
    
    # Проверяем, что введено число
    if not age_text.isdigit():
        await update.message.reply_text("Пожалуйста, введите число!")
        return AGE
    
    age = int(age_text)
    
    # Проверяем корректность возраста
    if age < 1 or age > 120:
        await update.message.reply_text("Пожалуйста, введите реальный возраст (1-120 лет)!")
        return AGE
    
    # Сохраняем возраст
    context.user_data['survey']['age'] = age
    
    await update.message.reply_text(
        "Отлично! Теперь выберите ваш пол:",
        reply_markup=get_gender_keyboard()
    )
    
    return GENDER

async def process_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка пола"""
    gender = update.message.text.strip()
    
    # Убираем эмодзи для чистоты данных
    clean_gender = gender.replace('👨', '').replace('👩', '').replace('🤷‍♂️', '').strip()
    context.user_data['survey']['gender'] = clean_gender
    
    await update.message.reply_text(
        "Отлично! Чем вы сейчас занимаетесь?",
        reply_markup=get_activity_keyboard()
    )
    
    return ACTIVITY

async def process_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка рода деятельности"""
    activity = update.message.text.strip()
    
    # Убираем эмодзи
    clean_activity = re.sub(r'[^\w\s/]', '', activity).strip()
    context.user_data['survey']['activity'] = clean_activity
    
    await update.message.reply_text(
        "🎯 Отлично! Теперь расскажите о ваших увлечениях.\n\n"
        "Вы можете выбрать несколько вариантов, нажимая на них.\n"
        "Когда закончите, нажмите '✅ Готово'.",
        reply_markup=get_hobbies_keyboard()
    )
    
    return HOBBIES

async def process_hobbies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка увлечений"""
    hobby = update.message.text.strip()
    
    if hobby == '✅ Готово':
        # Проверяем, выбраны ли увлечения
        hobbies_list = context.user_data['survey']['hobbies']
        if not hobbies_list:
            await update.message.reply_text(
                "Пожалуйста, выберите хотя бы одно увлечение!",
                reply_markup=get_hobbies_keyboard()
            )
            return HOBBIES
        
        # Формируем сводку
        survey_data = context.user_data['survey']
        summary = f"""
📊 Сводка ваших ответов:

👤 Ваш профиль: {survey_data['username']}
🎂 Возраст: {survey_data['age']} лет
🚻 Пол: {survey_data['gender']}
💼 Род деятельности: {survey_data['activity']}
🎨 Увлечения: {', '.join(hobbies_list)}

Верно ли все указано?

Напишите:
✅ Да - чтобы подтвердить
✏️ Нет - чтобы начать заново
        """
        
        await update.message.reply_text(summary)
        
        return CONFIRM
    
    else:
        # Добавляем увлечение (убираем эмодзи)
        clean_hobby = re.sub(r'[^\w\s]', '', hobby).strip()
        if clean_hobby and clean_hobby not in context.user_data['survey']['hobbies']:
            context.user_data['survey']['hobbies'].append(clean_hobby)
        
        # Показываем выбранные увлечения
        selected = context.user_data['survey']['hobbies']
        count = len(selected)
        
        await update.message.reply_text(
            f"✅ Выбрано увлечений: {count}\n"
            f"📝 Список: {', '.join(selected) if selected else 'пока нет'}\n\n"
            f"Можете выбрать еще или нажмите '✅ Готово'.",
            reply_markup=get_hobbies_keyboard()
        )
        
        return HOBBIES

async def confirm_survey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение и сохранение опроса"""
    user_response = update.message.text.strip().lower()
    
    if user_response in ['да', 'yes', '✅ да', 'подтвердить', 'готово']:
        # Сохраняем результат
        survey_data = context.user_data['survey']
        
        # Преобразуем список увлечений в строку для сохранения
        survey_data_copy = survey_data.copy()
        survey_data_copy['hobbies'] = ', '.join(survey_data['hobbies'])
        
        save_survey_result(survey_data_copy)
        
        await update.message.reply_text(
            "✅ Спасибо за участие в опросе!\n"
            "Ваши ответы сохранены анонимно.\n\n"
            "Чтобы начать новый опрос, нажмите /survey",
            reply_markup=None  # Убираем клавиатуру
        )
        
        # Очищаем данные
        if 'survey' in context.user_data:
            del context.user_data['survey']
        
        return ConversationHandler.END
    
    else:
        # Пользователь хочет изменить данные
        await update.message.reply_text(
            "Хорошо, давайте начнем заново!\n\n"
            "Сколько вам лет? (Введите число от 1 до 120)"
        )
        
        # Очищаем предыдущие данные (кроме базовой информации)
        if 'survey' in context.user_data:
            context.user_data['survey']['age'] = None
            context.user_data['survey']['gender'] = None
            context.user_data['survey']['activity'] = None
            context.user_data['survey']['hobbies'] = []
        
        return AGE

async def cancel_survey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена опроса"""
    if 'survey' in context.user_data:
        del context.user_data['survey']
    
    await update.message.reply_text(
        "Опрос отменен. Чтобы начать заново, нажмите /survey"
    )
    
    return ConversationHandler.END

async def skip_hobbies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пропуск выбора увлечений"""
    context.user_data['survey']['hobbies'] = ['Не указано']
    
    # Переходим к подтверждению
    survey_data = context.user_data['survey']
    summary = f"""
📊 Сводка ваших ответов:

👤 Ваш профиль: {survey_data['username']}
🎂 Возраст: {survey_data['age']} лет
🚻 Пол: {survey_data['gender']}
💼 Род деятельности: {survey_data['activity']}
🎨 Увлечения: Не указано

Верно ли все указано?

Напишите:
✅ Да - чтобы подтвердить
✏️ Нет - чтобы начать заново
    """
    
    await update.message.reply_text(summary)
    
    return CONFIRM