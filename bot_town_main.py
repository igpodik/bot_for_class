import logging
import random
import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext
from threading import Timer

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

# Список городов
cities = [
    "Абакан", "Абинск", "Александров", "Альметьевск", "Анапа", "Ангарск", "Арзамас", "Армавир", "Архангельск",
    "Астрахань", "Балаково", "Балахна", "Барнаул", "Белгород", "Бийск", "Благовещенск", "Братск", "Брянск",
    "Великие Луки", "Великий Новгород", "Владивосток", "Владикавказ", "Владимир", "Волгоград", "Вологда",
    "Воронеж", "Дзержинск", "Екатеринбург", "Елец", "Иваново", "Ижевск", "Йошкар-Ола", "Казань", "Калининград",
    "Калуга", "Кемерово", "Киров", "Кострома", "Краснодар", "Красноярск", "Курган", "Курск", "Липецк", "Магнитогорск",
    "Миасс", "Москва", "Мурманск", "Набережные Челны", "Нижневартовск", "Нижний Новгород", "Новокузнецк",
    "Новосибирск", "Ногинск", "Обнинск", "Омск", "Оренбург", "Орёл", "Пенза", "Пермь", "Петрозаводск", "Прокопьевск",
    "Псков", "Пятигорск", "Ростов-на-Дону", "Рыбинск", "Рязань", "Салават", "Самара", "Санкт-Петербург", "Саранск",
    "Саратов", "Серпухов", "Смоленск", "Сочи", "Ставрополь", "Старый Оскол", "Стерлитамак", "Сургут", "Сызрань",
    "Сыктывкар", "Таганрог", "Тамбов", "Тверь", "Тольятти", "Томск", "Тула", "Тюмень", "Улан-Удэ", "Ульяновск", "Уфа",
    "Чебоксары", "Челябинск", "Череповец", "Чита", "Энгельс", "Ярославль"
]
used_cities = []
attempts_limit = 5
timeout_seconds = 30
attempts = {}


async def start(update: Update, context: CallbackContext) -> None:
    """Handler for the /start command."""
    global used_cities, attempts
    used_cities = []
    attempts = {}
    keyboard = [[InlineKeyboardButton("Старт", callback_data="start_game")],
                [InlineKeyboardButton("Помощь", callback_data="help")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)


async def start_game(update: Update, context: CallbackContext) -> None:
    """Handler for starting the game."""
    global attempts
    next_city = random.choice(cities)
    used_cities.append(next_city)
    user_id = update.callback_query.from_user.id
    attempts[user_id] = 0
    await update.callback_query.message.edit_text(f"Мой город - {next_city}. Твой ход!")


async def game(update: Update, context: CallbackContext) -> None:
    """Handler for text messages."""
    global attempts

    # Получаем сообщение пользователя
    user_city = update.message.text.strip().capitalize()

    # Проверяем, что игра начата
    if not used_cities:
        await update.message.reply_text("Сначала начните игру с помощью команды /start.")
        return

    # Получаем последний город бота
    last_bot_city = used_cities[-1]

    # Проверяем, начинается ли город пользователя с правильной буквы
    if user_city[0].lower() != last_bot_city[-1].lower():
        await update.message.reply_text("Город должен начинаться на последнюю букву моего города!")
        return

    # Сбрасываем счётчик попыток игрока
    user_id = update.message.from_user.id
    if user_id in attempts:
        attempts[user_id] = 0

    # Проверяем, является ли город пользователя допустимым и не был ли он уже использован
    if user_city in cities and user_city not in used_cities:
        used_cities.append(user_city)

        # Находим следующий город для бота
        bot_next_city = [city for city in cities if
                         city[0].lower() == user_city[-1].lower() and city not in used_cities]

        if bot_next_city:
            bot_next_city = random.choice(bot_next_city)
            used_cities.append(bot_next_city)
            await update.message.reply_text(f"Мой город - {bot_next_city}. Твой ход!")
        else:
            await update.message.reply_text("Я проиграл! У меня больше нет городов на эту букву.")
    else:
        await update.message.reply_text("Такого города нет в списке или он уже был использован. Попробуйте другой.")

    # Увеличиваем счётчик попыток игрока
    attempts[user_id] += 1

    # Проверяем, достиг ли игрок предельного числа попыток
    if attempts[user_id] >= attempts_limit:
        await update.message.reply_text(f"Вы совершили слишком много ошибок ({attempts_limit}) и проиграли!")
        return

    # Устанавливаем таймер на ответ игрока
    await asyncio.sleep(timeout_seconds)
    if user_id in attempts and attempts[user_id] > 0:
        await update.message.reply_text(f"Вы не ответили в течение {timeout_seconds} секунд и проиграли!")


async def handle_timeout(update: Update, context: CallbackContext) -> None:
    """Handler for game timeout."""
    await update.message.reply_text("Время вышло. Начните новую игру с помощью команды /start.")


async def help_command(update: Update, context: CallbackContext) -> None:
    """Handler for the /help command."""
    help_text = "Правила игры:\n\n" \
                "1. Бот называет случайный город.\n" \
                "2. Игрок должен ответить городом, который начинается на последнюю букву предыдущего города.\n" \
                "3. Город не должен повторяться.\n" \
                "4. Если игрок не отвечает в течение 30 секунд, он проигрывает.\n" \
                "5. Если игрок называет город, которого нет в списке или который уже использовался, он проигрывает.\n" \
                "6. Игра продолжается до тех пор, пока у бота не закончатся города на последнюю букву."

    try:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(help_text)
    except (AttributeError, TypeError):
        logger.error("Could not reply to help command. Update object is None.")


def main() -> None:
    """Запуск бота."""

    TOKEN = '7033730122:AAGWI3-umvGtSbYt3ljoHuhr_NTwYPmAwWw'
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчики команд, кнопок и текстовых сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(start_game, pattern="start_game"))
    application.add_handler(CallbackQueryHandler(help_command, pattern="help"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, game))
    application.add_handler(MessageHandler(filters.Command, handle_timeout))

    # Запускаем бот
    application.run_polling()


if __name__ == '__main__':
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    main()
