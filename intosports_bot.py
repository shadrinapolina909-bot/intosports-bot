import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from datetime import datetime
import json
import os

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = "8916527707:AAGocCsvT8gPLrRkpTGXJkTP-sWOozsJ6pQ"

users_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name

    if user_id not in users_data:
        users_data[user_id] = {
            "name": user_name,
            "goal": None,
            "location": None,
            "level": None,
            "workouts": [],
            "meals": [],
            "weight": None,
            "subscribed": False,
            "created_at": datetime.now().isoformat()
        }

    keyboard = [
        [InlineKeyboardButton("🎯 Выбрать цель", callback_data="choose_goal")],
        [InlineKeyboardButton("💪 Получить тренировку", callback_data="get_workout")],
        [InlineKeyboardButton("🍽️ Анализ питания", callback_data="food_analysis")],
        [InlineKeyboardButton("📊 Мой прогресс", callback_data="progress")],
        [InlineKeyboardButton("💳 Подписка", callback_data="subscribe")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"🏋️ Привет, {user_name}! 💪\n\n"
        "Я твой персональный AI-коуч. Помогу тебе:\n"
        "✅ Подобрать тренировки\n"
        "✅ Проанализировать питание\n"
        "✅ Отследить прогресс\n\n"
        "Давай начнём! Выбери, что тебе нужно:",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "choose_goal":
        keyboard = [
            [InlineKeyboardButton("📉 Похудеть", callback_data="goal_lose")],
            [InlineKeyboardButton("💪 Набрать мышцу", callback_data="goal_gain")],
            [InlineKeyboardButton("✨ Здоровье и тонус", callback_data="goal_health")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🎯 Какая у тебя цель?",
            reply_markup=reply_markup
        )

    elif query.data == "goal_lose":
        users_data[user_id]["goal"] = "худеть"
        await choose_location(query, user_id)
    elif query.data == "goal_gain":
        users_data[user_id]["goal"] = "набрать_массу"
        await choose_location(query, user_id)
    elif query.data == "goal_health":
        users_data[user_id]["goal"] = "здоровье"
        await choose_location(query, user_id)

    elif query.data == "get_workout":
        await get_workout(query, user_id)
    elif query.data == "food_analysis":
        await query.edit_message_text(
            "🍽️ Отправь фото своего блюда\n"
            "Я проанализирую калории и макросы!"
        )
    elif query.data == "progress":
        await show_progress(query, user_id)
    elif query.data == "subscribe":
        await show_subscribe(query)

async def choose_location(query, user_id):
    keyboard = [
        [InlineKeyboardButton("🏠 Дома", callback_data="loc_home")],
        [InlineKeyboardButton("🏋️ В зале", callback_data="loc_gym")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "📍 Где ты будешь тренироваться?",
        reply_markup=reply_markup
    )

async def get_workout(query, user_id):
    user = users_data.get(user_id, {})
    goal = user.get("goal", "неизвестно")

    workouts = {
        "худеть": "🔥 КАРДИО-ТРЕНИРОВКА\n\n1️⃣ Прыжки на скакалке 30 сек\n2️⃣ Бёрпи 20 раз\n3️⃣ Прыжки в сторону 30 сек\n\nПовторить 3 раза с отдыхом 1 мин",
        "набрать_массу": "💪 СИЛОВАЯ ТРЕНИРОВКА\n\n1️⃣ Приседания 4x10\n2️⃣ Жим лёжа 4x8\n3️⃣ Тяга 3x10\n\nОтдых между подходами 2 минуты",
        "здоровье": "✨ ФУНКЦИОНАЛЬНАЯ ТРЕНИРОВКА\n\n1️⃣ Отжимания 3x10\n2️⃣ Приседания 3x15\n3️⃣ Планка 3x30сек\n\nВыполняй 3 раза в неделю"
    }

    workout = workouts.get(goal, "Сначала выбери цель!")

    keyboard = [
        [InlineKeyboardButton("✅ Выполнил", callback_data="workout_done")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(workout, reply_markup=reply_markup)

async def show_progress(query, user_id):
    user = users_data.get(user_id, {})
    workouts_count = len(user.get("workouts", []))

    progress_text = (
        f"📊 ТВОЙ ПРОГРЕСС\n\n"
        f"📅 Дата регистрации: {user.get('created_at', 'неизвестно')[:10]}\n"
        f"🎯 Цель: {user.get('goal', 'не выбрана')}\n"
        f"💪 Выполнено тренировок: {workouts_count}\n"
        f"⚖️ Вес: {user.get('weight', 'не указан')} кг\n\n"
        f"Продолжай в том же духе! 🔥"
    )

    keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(progress_text, reply_markup=reply_markup)

async def show_subscribe(query):
    subscribe_text = (
        "💳 ПОДПИСКА\n\n"
        "📌 БАЗОВАЯ - $7/месяц\n"
        "✅ 3 готовых плана\n"
        "✅ Ежедневные тренировки\n"
        "✅ Дневник упражнений\n\n"
        "🌟 ПРЕМИУМ - $17/месяц\n"
        "✅ Персональная программа\n"
        "✅ Анализ питания\n"
        "✅ Отслеживание прогресса\n"
        "✅ Еженедельные коррекции\n\n"
        "Выбирай подписку и начни трансформацию! 🚀"
    )

    keyboard = [
        [InlineKeyboardButton("Базовая ($7)", url="https://example.com/basic")],
        [InlineKeyboardButton("Премиум ($17)", url="https://example.com/premium")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(subscribe_text, reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    await update.message.reply_text(
        "📸 Спасибо! Я получил твое сообщение.\n"
        "Пока я учусь анализировать фото еды. Скоро смогу! 🤖"
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
