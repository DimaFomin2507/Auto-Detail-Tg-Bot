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
    bot.send_message(message.chat.id, f'Привет! {message.from_user.first_name}' "👋Добро пожаловать в Vaz-Details! \n"
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