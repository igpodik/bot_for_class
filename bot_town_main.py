import logging
import random
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

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

async def start(update: ContextTypes.DEFAULT_TYPE, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Давай сыграем в игру в города. Напиши название города.")

async def game(update: ContextTypes.DEFAULT_TYPE, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений."""
    text = update.message.text.strip().capitalize()

    # Проверяем, что название города начинается на последнюю букву предыдущего города
    if used_cities:
        last_city = used_cities[-1]
        if text[0] != last_city[-1]:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Город должен начинаться на последнюю букву предыдущего города!")
            return

    # Проверяем, что город есть в списке и он еще не использован
    if text in cities and text not in used_cities:
        used_cities.append(text)
        # Выбираем случайный город на последнюю букву введенного города
        valid_cities = [city for city in cities if city[0] == text[-1] and city not in used_cities]
        if valid_cities:
            next_city = random.choice(valid_cities)
            used_cities.append(next_city)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Мой город - {next_city}. Твой ход!")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="У меня закончились города на эту букву. Ты выиграл!")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Некорректный город или он уже был использован.")

def main() -> None:
    """Запуск бота."""
    TOKEN = '7033730122:AAGWI3-umvGtSbYt3ljoHuhr_NTwYPmAwWw'
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчики команд и текстовых сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, game))

    # Запускаем бот
    application.run_polling()

if __name__ == '__main__':
    main()
