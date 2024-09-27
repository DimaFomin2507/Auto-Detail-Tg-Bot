import psycopg2
import telebot
from telebot import types
from telebot import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '7390952682:AAGwjw7x7JU07V2w-wjD2ATaR1y8meHGnDE'
bot = telebot.TeleBot(API_TOKEN,)


DATABASE_URL = 'postgresql://Auto-Details:1234@tgbot:5432/users_auto_details'

# States for the FSM
class UserStates(types.InlineKeyboardMarkup):
    CONFIRMATION = 'confirmation'
    MODEL = 'model'
    NUMBER = 'number'
    DATE = 'date'
    TYPE = 'type'
    SERVICE = 'service'
    CONFIRM = 'confirm'
    CONTACT = 'contact'

# Dictionary to store user data
user_data = {}

# ----------------------- Handlers -----------------------

def get_db_connection():
    """Функция для получения соединения с PostgreSQL."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except (Exception, psycopg2.Error) as error:
        print("Ошибка при подключении к базе данных PostgreSQL:", error)
        return None

@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('Записаться на ТО'))
    bot.send_message(message.chat.id,
                     "👋 Здравствуйте! Вас приветствует Auto-Detail_Bot,\n"
                     " Хотите записаться на ТО?", reply_markup=markup)

# Handle the "Записаться на ТО" button click
@bot.message_handler(func=lambda message: message.text == "Записаться на ТО")
def handle_appointment(message):
    # Hide the keyboard and ask for car model
    bot.send_message(message.chat.id,
                     "🚗 Введите марку и модель автомобиля (например, Toyota Camry):",
                     reply_markup=types.ReplyKeyboardRemove())

    # Set state to MODEL
    bot.set_state(message.chat.id, UserStates.MODEL)

    # Register the next step handler to get the car model
    bot.register_next_step_handler(message, get_car_model)

# Get car model from user
def get_car_model(message):
    user_data[message.chat.id] = {} # Initialize user data
    user_data[message.chat.id]['model'] = message.text

    bot.send_message(message.chat.id, f"👌 Отлично! Марка и модель: {user_data[message.chat.id]['model']}\n"
                                   f"Теперь введите госномер автомобиля:")

    # Set state to NUMBER
    bot.set_state(message.chat.id, UserStates.NUMBER)

    bot.register_next_step_handler(message, generate_calendar)

# Get car number from user
def generate_calendar(year=None, month=None):
    """Generates an inline calendar keyboard."""
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month

    # Get the first and last days of the month
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, 1) + timedelta(days=32)

    # Create the inline keyboard
    markup = InlineKeyboardMarkup(row_width=7)

    # Add previous and next month buttons
    if month > 1:
        markup.add(InlineKeyboardButton("<<", callback_data=f"prev_{year}_{month - 1}"))
    else:
        markup.add(InlineKeyboardButton("<<", callback_data=f"prev_{year - 1}_{12}"))
    markup.add(InlineKeyboardButton(f"{datetime(year, month, 1).strftime('%B')} {year}", callback_data="current"))
    if month < 12:
        markup.add(InlineKeyboardButton(">>", callback_data=f"next_{year}_{month + 1}"))
    else:
        markup.add(InlineKeyboardButton(">>", callback_data=f"next_{year + 1}_{1}"))

    # Add days of the week
    markup.add(*[InlineKeyboardButton(day.strftime('%a'), callback_data="week") for day in [first_day + timedelta(days=i) for i in range(7)]])

    # Add days of the month
    for day in range(1, 32):
        current_day = first_day + timedelta(days=day)
        if current_day.month == month:
            markup.add(InlineKeyboardButton(str(current_day.day), callback_data=f"{current_day.strftime('%Y-%m-%d')}"))
        else:
            break
    return markup

# Handle date and time input
@bot.message_handler(func=lambda message: bot.get_state(message.chat.id) == UserStates.DATE)
def get_date_and_time(message):
    # Send the calendar
    bot.send_message(message.chat.id, "📅 Выберите дату:", reply_markup=generate_calendar())

    # Set state to DATE
    bot.set_state(message.chat.id, UserStates.DATE)

    # Register the next step handler to get the date and time
    # (The handler will be called when the user clicks a date button)
    # bot.register_next_step_handler(message, get_time)

# Handle calendar button clicks
@bot.callback_query_handler(func=lambda call: True)
def handle_calendar_click(call):
    # Get the user's state
    user_state = bot.get_state(call.message.chat.id)

    if user_state == UserStates.DATE:
        # Handle date selection
        if call.data.startswith("prev") or call.data.startswith("next"):
            # Update the calendar
            year, month = [int(x) for x in call.data.split('_')[1:]]
            new_calendar = generate_calendar(year, month)
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=new_calendar)
        elif call.data == "current":
            # Do nothing
            pass
        elif call.data.isdigit():
            # User selected a date
            selected_date = call.data
            user_data[call.message.chat.id]['date'] = selected_date
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                   text=f"📅 Вы выбрали дату: {selected_date}\n"
                                   f"Теперь введите время (например, 14:00):")
            bot.set_state(call.message.chat.id, UserStates.DATE)
            bot.register_next_step_handler(call.message, get_time)


@bot.message_handler(func=lambda message: bot.get_state(message.chat.id) == UserStates.DATE)
def get_time(message):
    try:
        # Extract the time from the user's input
        time_obj = datetime.strptime(message.text, '%H:%M').time()

        # Construct the date and time string
        date_and_time_str = f"{user_data[message.chat.id]['date']} {time_obj.strftime('%H:%M')}"
        user_data[message.chat.id]['date'] = date_and_time_str

        # Display a confirmation of the date and time
        bot.send_message(message.chat.id, f"📅 Вы выбрали: {date_and_time_str}")

        # Proceed to the next step
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton('Плановое'),
                   types.KeyboardButton('Срочное'),
                   types.KeyboardButton('Техническое'))
        bot.send_message(message.chat.id, "🔧 Какой тип ТО Вам нужен?", reply_markup=markup)

        # Set state to SERVICE
        bot.set_state(message.chat.id, UserStates.SERVICE)
        bot.register_next_step_handler(message, get_service_type)

    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат времени. Пожалуйста, введите время в формате HH:MM.")
        bot.register_next_step_handler(message, get_time)

# Get service type from user
@bot.message_handler(func=lambda message: bot.get_state(message.chat.id) == UserStates.SERVICE)
def get_service_type(message):
    user_data[message.chat.id]['service'] = message.text

    # Confirmation message
    confirmation_msg = f"""
    ✅ Подтвердите вашу запись:

    Модель: {user_data[message.chat.id]['model']}
    Госномер: {user_data[message.chat.id]['number']}
    Дата и время: {user_data[message.chat.id]['date']} 
    Тип ТО: {user_data[message.chat.id]['service']}

    Все верно?
    """

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('Да'), types.KeyboardButton('Нет'))
    bot.send_message(message.chat.id, confirmation_msg, reply_markup=markup)

    # Set state to CONFIRMATION
    bot.set_state(message.chat.id, UserStates.CONFIRMATION)

    bot.register_next_step_handler(message, process_confirmation)

# Process confirmation from user
@bot.message_handler(func=lambda message: bot.get_state(message.chat.id) == UserStates.CONFIRMATION)
def process_confirmation(message):
    if message.text == 'Да':
        # Save appointment to database or perform other actions
        bot.send_message(message.chat.id, "🎉 Отлично! Ваша запись успешно создана. Мы свяжемся с Вами для подтверждения.")
    else:
        bot.send_message(message.chat.id, "😔 Пожалуйста, попробуйте снова.")

    # Reset state
    bot.delete_state(message.chat.id)

    # Clear user data
    del user_data[message.chat.id]

if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
#
