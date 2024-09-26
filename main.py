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


