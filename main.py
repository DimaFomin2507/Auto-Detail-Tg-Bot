import json

import telebot
from telebot import types
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from handlers import user_data
from settings import API_TOKEN

bot = telebot.TeleBot(API_TOKEN, )


# Определение состояния пользователя — не путать с классом, наследованным от InlineKeyboardMarkup
class UserStates:
    CONFIRMATION = 'confirmation'
    MODEL = 'model'
    NUMBER = 'number'
    CHOOSING_YEAR = 1
    CHOOSING_MONTH = 2
    CHOOSING_DAY = 3
    SERVICE = 'service'
    CONFIRM = 'confirm'
    CONTACT = 'contact'


@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('Записаться на ТО'))
    bot.send_message(message.chat.id,
                     f"👋 Здравствуйте {message.from_user.first_name}! Вас приветствует Auto-Detail_Bot,\n"
                     "Хотите записаться на ТО?", reply_markup=markup)


# Handle the "Записаться на ТО" button click
@bot.message_handler(func=lambda message: message.text == "Записаться на ТО")
def handle_appointment(message):
    # Hide the keyboard and ask for car model
    bot.send_message(message.chat.id,
                     "🚗 Введите марку и модель вашего автомобиля:",
                     reply_markup=types.ReplyKeyboardRemove())

    # Set state to MODEL
    if message.chat.id not in user_data:
        user_data[message.chat.id] = {}
    user_data[message.chat.id]['state'] = UserStates.MODEL

    # Register the next step handler to get the car model
    bot.register_next_step_handler(message, get_car_model)


# Get car model from user
def get_car_model(message):
    user_data[message.chat.id]['model'] = message.text

    bot.send_message(
        message.chat.id,
        f"👌 Отлично! Марка и модель: {user_data[message.chat.id]['model']}\n"
        f"Теперь введите госномер автомобиля(Х111ХХ136/36):"
    )

    # Установка состояния пользователя
    user_data[message.chat.id]['state'] = UserStates.NUMBER

    bot.register_next_step_handler(message, get_car_number)


def get_car_number(message):
    user_data[message.chat.id]['number'] = message.text

    bot.send_message(
        message.chat.id,
        f"Марка и модель: {user_data[message.chat.id]['model']}\n"
        f"Госномер: {user_data[message.chat.id]['number']}\n"
        f"Пожалуйста, выберите год:"
    )

    # Отправить клавиатуру с выбором года
    bot.send_message(message.chat.id, "Выберите год:", reply_markup=generate_years())


# Функция генерации кнопок для выбора года
def generate_years():
    markup = InlineKeyboardMarkup()
    current_year = datetime.now().year
    for year in range(current_year, current_year + 2):
        markup.add(InlineKeyboardButton(text=str(year), callback_data=f"year_{year}"))
    return markup


# Функция генерации кнопок для выбора месяца
def generate_months():
    markup = InlineKeyboardMarkup()
    months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь',
              'Декабрь']
    for i, month in enumerate(months, start=1):
        markup.add(InlineKeyboardButton(text=month, callback_data=f"month_{i}"))
    return markup


def generate_calendar(year, month):
    markup = InlineKeyboardMarkup()
    num_days = (datetime(year, month % 12 + 1, 1) - timedelta(days=1)).day
    for day in range(1, num_days + 1):
        markup.add(InlineKeyboardButton(text=str(day), callback_data=f"date_{year}_{month}_{day}"))
    return markup


# Обработчик выбора года


@bot.callback_query_handler(func=lambda call: call.data.startswith('year_'))
def year_callback(call):
    chat_id = call.message.chat.id
    year = call.data.split('_')[1]
    user_data[chat_id]['year'] = year
    user_data[chat_id]['state'] = UserStates.CHOOSING_MONTH

    markup = types.InlineKeyboardMarkup(row_width=4)
    months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
              'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']

    # Генерируем кнопки в цикле, используя f-строки для callback_data
    markup.add(*[types.InlineKeyboardButton(month, callback_data=f'month_{i:02}') for i, month in enumerate(months, 1)])

    bot.send_message(chat_id, "Выберите месяц:", reply_markup=markup)


# Обработчик выбора месяца

@bot.callback_query_handler(func=lambda call: call.data.startswith('month_'))
def month_callback(call):
    chat_id = call.message.chat.id
    month = call.data.split('_')[1]
    user_data[chat_id]['month'] = month
    user_data[chat_id]['state'] = UserStates.CHOOSING_DAY

    markup = types.InlineKeyboardMarkup(row_width=7)  # Кнопки в ряд по 7 дней
    days = [str(i) for i in range(1, 31)]  # Генерируем дни числами

    # Создаем кнопки дней с помощью спискового включения
    buttons = [types.InlineKeyboardButton(day, callback_data=f'date_{user_data[chat_id]["year"]}_{month}_{day}') for day
               in days]
    markup.add(*buttons)  # Распаковываем список кнопок в markup.add()

    bot.send_message(chat_id, "Выберите день:", reply_markup=markup)


# Обработчик выбора дня
@bot.callback_query_handler(func=lambda call: call.data.startswith('date_'))
def date_callback(call):
    chat_id = call.message.chat.id
    try:
        _, year, month, day = call.data.split('_')
        user_data[chat_id]['year'] = year
        user_data[chat_id]['month'] = month
        user_data[chat_id]['day'] = day

        bot.send_message(chat_id, f"Вы выбрали дату: {day}.{month}.{year}\nПожалуйста, подтвердите запись.")
        user_data[chat_id]['state'] = UserStates.CONFIRMATION

        confirm_markup = types.InlineKeyboardMarkup()
        confirm_markup.add(types.InlineKeyboardButton('Подтвердить запись', callback_data='confirm'))
        bot.send_message(chat_id, "Подтвердите вашу запись:", reply_markup=confirm_markup)

    except ValueError:
        bot.send_message(chat_id, "Произошла ошибка при выборе даты. Пожалуйста, попробуйте снова.")


# Обработчик подтверждения записи
@bot.callback_query_handler(func=lambda call: call.data == 'confirm')
def confirm_callback(call: CallbackQuery):
    chat_id = call.message.chat.id
    # Логика подтверждения
    with open(call.from_user.first_name + "_" +  datetime.now().strftime('%Y.%m.%d') + '.json', 'w',
              encoding='utf-8') as f:
        json.dump(user_data[chat_id], f, ensure_ascii=False, indent=4)
    bot.send_message(chat_id, "🎉 Отлично! Ваша запись успешно создана. Мы свяжемся с Вами для подтверждения.")


if __name__ == "__main__":
    bot.polling(none_stop=True)
