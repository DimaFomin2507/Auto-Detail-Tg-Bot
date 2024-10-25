import telebot
from telebot import types

bot = telebot.TeleBot('7390952682:AAGwjw7x7JU07V2w-wjD2ATaR1y8meHGnDE')

MODEL, NUMBER, DATE, CONFIRM = range(4)
def create_buttons(text1, text2):
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text1, callback_data=text1)
    button2 = types.InlineKeyboardButton(text2, callback_data=text2)
    keyboard.add(button1, button2)
    return keyboard
@bot.message_handler(commands=['start', 'main', 'hello'])
def start_command(message):
    bot.send_message(message.chat.id, f'Привет! {message.from_user.first_name}' 
                                      "🚗Здесь вам помогут записаться на ТО вашего автомоблия.\n", 'Для заполнения данных нажмите',
                                        reply_markup=create_buttons("Записаться на ТО", "Отмена"))




@bot.message_handler(commands=['help'])
def main(message):
    bot.send_message(message.chat.id, "Как записаться в 'Vaz-Details':\n "
                                      "1. Выберите доступно в нашем каталоге.\n"
                                      "2. Добавьте их в корзину.\n"
                                      "3. Введите ваши контактные данные (имя, телефон, адрес).\n"
                                      "4. Выберите способ доставки и оплаты.\n"
                                      "5. Подтвердите заказ.\n"
                                      " Мы поможем вам подобрать правильные запчасти для вашей модели ВАЗ!\n"
                                      "Свяжитесь с нами, если у вас возникли вопросы:'Контаdкты'")


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == 'Записаться на ТО':
        bot.send_message(call.message.chat.id, "Введите модель вашего автомобиля:")
        bot.set_state(call.message.chat.id, MODEL, call.message.chat.id)
    elif call.data == "Отменить":
        bot.send_message(call.message.chat.id, "Запись отменена.")
        bot.delete_state(call.message.chat.id, call.message.chat.id)
    elif call.data == "Подтвердить":
        # Сохраните запись в базу данных или обработайте ее
        bot.send_message(call.message.chat.id, "✅ Ваша запись на ТО подтверждена! Мы ждем вас {date} в {time} по адресу: улица Антонова-Овсеенко, 37А.".
                                format(date=call.message.data['date'], time="время"))
        bot.delete_state(call.message.chat.id, call.message.chat.id)
    elif call.data == 'Отмена':
        bot.send_message(call.message.chat.id, "Отмена")
        bot.delete_state(call.message.chat.id, call.message.chat.id)


@bot.message_handler(func=lambda message: bot.get_state(message.chat.id) == MODEL)
def get_model(message):
    bot.set_state(message.chat.id, NUMBER, message.chat.id)
    bot.send_message(message.chat.id, "Введите госномер автомобиля:")
    bot.set_state(message.chat.id, NUMBER, message.chat.id)
    bot.message.data['model'] = message.text

@bot.message_handler(func=lambda message: bot.get_state(message.chat.id) == NUMBER)
def get_number(message):
    bot.set_state(message.chat.id, DATE, message.chat.id)
    bot.send_message(message.chat.id, "Введите желаемую дату и время ТО (ДД.ММ.ГГГГ ЧЧ:ММ):")
    bot.message.data['number'] = message.text

@bot.message_handler(func=lambda message:bot.get_state(message.chat.id) == DATE)
def get_date(message):
    bot.set_state(message.chat.id, CONFIRM, message.chat.id)
    bot.message.data['date'] = message.text
    text = "✅ Подтвердите вашу запись:\n\n" \
              "Модель: {model}\n" \
              "Госномер: {number}\n" \
              "Дата и время: {date}\n\n" \
              "Все верно?".format(
        model=bot.message.data['model'],
        number=bot.message.data['number'],
        date=bot.message.data['date']
    )
    bot.send_message(message.chat.id, text, reply_markup=create_buttons("Подтвердить", "Отменить"))

bot.polling(non_stop=True)




import asyncio
from aiogram.dispatcher.fsm.storage import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram import Bot, Dispatcher, types

# Токен вашего бота
API_TOKEN = '7390952682:AAGwjw7x7JU07V2w-wjD2ATaR1y8meHGnDE'

# Создание бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Создание состояний для FSM
class RecordStates(StatesGroup):
    model = State()
    number = State()
    date = State()
    confirm = State()


# Функция для создания кнопок
def create_buttons(text1, text2):
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text1, callback_data=text1)
    button2 = types.InlineKeyboardButton(text2, callback_data=text2)
    keyboard.add(button1, button2)
    return keyboard

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer("👋 Привет! Хотите записаться на ТО для вашего авто? 🚗", reply_markup=create_buttons("Записаться на ТО", "Отмена"))

# Обработчик кнопок
@dp.callback_query_handler(state='*')
async def handle_callback(call: types.CallbackQuery, state: FSMContext):
    if call.data == "Записаться на ТО":
        await call.message.answer("Введите модель вашего автомобиля!: ")
        await RecordStates.model.set()
    elif call.data == "Отменить":
        await call.message.answer("Запись отменена.")
        await state.finish()
    elif call.data == "Отменить":
        data = await state.get_data()
        await call.message.answer("✅ Ваша запись на ТО подтверждена! Мы ждем вас {date} в {time} по адресу [адрес сервиса].".format(date=data['date'], time="время"))
        await state.finish()
    elif call.data == 'Отмена':
        await call.message.answer("Отмена")
        await state.finish()

# Обработчики состояний
@dp.message_handler(state=RecordStates.model)
async def get_model(message: types.Message, state: FSMContext):
    await state.update_data(model=message.text)
    await message.answer("Введите госномер автомобиля: ")
    await RecordStates.next()

@dp.message_handler(state=RecordStates.number)
async def get_number(message: types.Message, state: FSMContext):
    await state.update_data(number=message.text)
    await message.answer("Введите желаемую дату и время ТО (ДД.ММ.ГГГГ ЧЧ:ММ):")
    await RecordStates.next()

@dp.message_handler(state=RecordStates.date)
async def get_date(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text)
    data = await state.get_data()
    text = "✅ Подтвердите вашу запись:\n\n" \
              "Модель: {model}\n" \
              "Госномер: {number}\n" \
              "Дата и время: {date}\n\n" \
              "Все верно?".format(model=data['model'], number=data['number'], date=data['date'])
    await message.answer(text, reply_markup=create_buttons("Подтвердить", "Отменить"))
    await RecordStates.next()


# Запуск бота
async def main():
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())





import telebot
from aiogram.fsm.context import FSMContext
from telebot import types, State

API_TOKEN = '7390952682:AAGwjw7x7JU07V2w-wjD2ATaR1y8meHGnDE'
bot = telebot.TeleBot(API_TOKEN)

# States for the FSM
class UserStates(types.StatesGroup):
    MODEL = State()
    NUMBER = State()
    DATE = State()
    CONFIRM = State()

# Dictionary to store user data
user_data = {}

@bot.message_handler(commands=['start'])
def start(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('Записаться на ТО'))
    bot.send_message(message.chat.id, "👋 Привет! Хотите записаться на ТО?", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Записаться на ТО')
def schedule_service(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton('Lada Vesta'), types.KeyboardButton('Lada Granta'))
    markup.add(types.KeyboardButton('Lada Largus'), types.KeyboardButton('Lada XRAY'))
    bot.send_message(message.chat.id, "🚗 Какую модель Вы хотите записать?", reply_markup=markup)
    bot.set_state(message.chat.id, UserStates.MODEL)

@bot.message_handler(state=UserStates.MODEL)
def get_model(message: types.Message, state: FSMContext):
    user_data[message.chat.id] = {'model': message.text}
    bot.send_message(message.chat.id, "👌 Отлично! А теперь введите госномер Вашего автомобиля:")
    bot.set_state(message.chat.id, UserStates.NUMBER)

@bot.message_handler(state=UserStates.NUMBER)
def get_number(message: types.Message, state: FSMContext):
    user_data[message.chat.id]['number'] = message.text
    bot.send_message(message.chat.id, "📅 Когда Вы бы хотели записаться? Укажите дату и время (например, 2024-03-15 14:00):")
    bot.set_state(message.chat.id, UserStates.DATE)

@bot.message_handler(state=UserStates.DATE)
def get_date(message: types.Message, state: FSMContext):
    user_data[message.chat.id]['date'] = message.text

    # Prepare confirmation message
    text = "✅ Подтвердите вашу запись:\n\n" \
            "Модель: {model}\n" \
            "Госномер: {number}\n" \
            "Дата и время: {date}\n\n" \
            "Все верно?".format(
            model=user_data[message.chat.id]['model'],
            number=user_data[message.chat.id]['number'],
            date=user_data[message.chat.id]['date']
        )

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton('Да'), types.KeyboardButton('Нет'))
    bot.send_message(message.chat.id, text, reply_markup=markup)
    bot.set_state(message.chat.id, UserStates.CONFIRM)

@bot.message_handler(state=UserStates.CONFIRM)
def confirm_appointment(message: types.Message, state: FSMContext):
    if message.text == 'Да':
        bot.send_message(message.chat.id, "🎉 Отлично! Ваша запись успешно создана. Мы свяжемся с Вами для подтверждения.")
        bot.delete_state(message.chat.id)
    else:
        bot.send_message(message.chat.id, "😔 Попробуйте еще раз.")
        bot.delete_state(message.chat.id)

bot.polling(none_stop=True, interval=0)















import psycopg2
import telebot
from telebot import types
from telebot import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


bot = telebot.TeleBot('7390952682:AAGwjw7x7JU07V2w-wjD2ATaR1y8meHGnDE')


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

MODEL, NUMBER, DATE, CONFIRM = range(4)
def create_buttons(text1, text2):
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text1, callback_data=text1)
    button2 = types.InlineKeyboardButton(text2, callback_data=text2)
    keyboard.add(button1, button2)
    return keyboard

@bot.message_handler(commands=['start','main', 'hello'])
def start(message: telebot.types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('Записаться на ТО'))
    bot.send_message(message.chat.id,
                     "👋 Здравствуйте! Вас приветствует Auto-Detail_Bot,\n"
                     " Хотите записаться на ТО?", reply_markup=markup)


# Handle the "Записаться на ТО" button click
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == 'Записаться на ТО':
        bot.send_message(call.message.chat.id, "Введите модель вашего автомобиля:")
        bot.set_state(call.message.chat.id, MODEL, call.message.chat.id)
    elif call.data == "Отменить":
        bot.send_message(call.message.chat.id, "Запись отменена.")
        bot.delete_state(call.message.chat.id, call.message.chat.id)
    elif call.data == "Подтвердить":
        # Сохраните запись в базу данных или обработайте ее
        bot.send_message(call.message.chat.id, "✅ Ваша запись на ТО подтверждена! Мы ждем вас {date} в {time} по адресу: улица Антонова-Овсеенко, 37А.".
                                format(date=call.message.data['date'], time="время"))
        bot.delete_state(call.message.chat.id, call.message.chat.id)
    elif call.data == 'Отмена':
        bot.send_message(call.message.chat.id, "Отмена")
        bot.delete_state(call.message.chat.id, call.message.chat.id)


@bot.message_handler(func=lambda message: bot.get_state(message.chat.id) == MODEL)
def get_model(message):
    bot.set_state(message.chat.id, NUMBER, message.chat.id)
    bot.send_message(message.chat.id, "Введите госномер автомобиля:")
    bot.set_state(message.chat.id, NUMBER, message.chat.id)
    bot.message.data['model'] = message.text

@bot.message_handler(func=lambda message: bot.get_state(message.chat.id) == NUMBER)
def get_number(message):
    bot.set_state(message.chat.id, DATE, message.chat.id)
    bot.send_message(message.chat.id, "Введите желаемую дату и время ТО (ДД.ММ.ГГГГ ЧЧ:ММ):")
    bot.message.data['number'] = message.text

@bot.message_handler(func=lambda message:bot.get_state(message.chat.id) == DATE)
def get_date(message):
    bot.set_state(message.chat.id, CONFIRM, message.chat.id)
    bot.message.data['date'] = message.text
    text = "✅ Подтвердите вашу запись:\n\n" \
              "Модель: {model}\n" \
              "Госномер: {number}\n" \
              "Дата и время: {date}\n\n" \
              "Все верно?".format(
        model=bot.message.data['model'],
        number=bot.message.data['number'],
        date=bot.message.data['date']
    )
    bot.send_message(message.chat.id, text, reply_markup=create_buttons("Подтвердить", "Отменить"))
    bot.set_state(message.chat.id, UserStates.CONFIRMATION)

    bot.register_next_step_handler(message, process_confirmation)

    # Confirmation message


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

@bot.message_handler(commands=['help'])
def main(message):
    bot.send_message(message.chat.id, "Как записаться в 'Vaz-Details':\n "
                                      "1. Выберите доступно в нашем каталоге.\n"
                                      "2. Добавьте их в корзину.\n"
                                      "3. Введите ваши контактные данные (имя, телефон, адрес).\n"
                                      "4. Выберите способ доставки и оплаты.\n"
                                      "5. Подтвердите заказ.\n"
                                      " Мы поможем вам подобрать правильные запчасти для вашей модели ВАЗ!\n"
                                      "Свяжитесь с нами, если у вас возникли вопросы:'Контакты'")

if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)












import psycopg2
import telebot
from telebot import types
from telebot import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


bot = telebot.TeleBot('7390952682:AAGwjw7x7JU07V2w-wjD2ATaR1y8meHGnDE')


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

@bot.message_handler(commands=['start','main', 'hello'])
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
