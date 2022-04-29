import telebot
from telebot import types
from pyowm import OWM
from datetime import date, datetime
import sqlite3
import config

def get_weather(city_request):
    # 2688b7df83a041e23c5602ce56441616
    owm = OWM(config.TOKEN)
    mgr = owm.weather_manager()

    try:
        observation = mgr.weather_at_place(city_request)
        w = observation.weather

        temperature = w.temperature('celsius')
        wind = w.wind()['speed']
        humidity = w.humidity
        clouds = w.clouds
        pressure = w.pressure['press']
        visibility = w.visibility_distance

        data = f"\nПогода в {city_request} на {date.today().strftime('%d/%m/%Y')}:\n\n" \
               f"- текущая температура: {temperature['temp']} C\n" \
               f"- максимальная температура: {temperature['temp_max']} C\n" \
               f"- минимальная температура: {temperature['temp_min']} C\n" \
               f"- ощущается как: {temperature['feels_like']} C\n" \
               f"- ветер: {wind} м/сек\n" \
               f"- влажность: {humidity} г/м3\n" \
               f"- облачность: {clouds} %\n" \
               f"- давление: {pressure} мм рт.ст\n" \
               f"- видимость: {visibility} м\n"
    except Exception:
        data = 'Некорректный ввод'

    return data


def add_info(message):
    con = sqlite3.connect('wheater_users.db')
    cur = con.cursor()

    newTable = """CREATE TABLE IF NOT EXISTS tbot_users (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        firstname VARCHAR (25),
        lastname  VARCHAR (25),
        username  VARCHAR (25),
        date      DATETIME);
    """
    cur.execute(newTable)
    con.commit()

    sql = f"INSERT INTO tbot_users (firstname, lastname, username, date) " \
          f"VALUES ('{message.from_user.first_name}', " \
          f"'{message.from_user.last_name}', " \
          f"'{message.from_user.username}', " \
          f"'{datetime.now()}')"

    with con:
        cur.execute(sql)


bot = telebot.TeleBot("5147548874:AAGjoYLJm0x_2ppDLavPOUE0EgliIMfB8AE")


@bot.message_handler(commands=['help'])
def info(message):
    bot.send_message(message.chat.id,
                     f'{message.from_user.first_name},\n'
                     f'- Вы можете прислать мне фото (перетяните сюда)')


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     f'Привет, {message.from_user.first_name}, '
                     f'этот бот умеет показывать погоду в любом городе.\n'
                     f'Дополнительно в /help')
    markup = types.InlineKeyboardMarkup()
    item5 = types.InlineKeyboardButton("Да", callback_data="yes")
    item6 = types.InlineKeyboardButton("Нет", callback_data="no")
    markup.add(item5, item6)
    bot.send_message(message.chat.id, text='Продолжаем?', reply_markup=markup)
    add_info(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == "yes":
            bot.send_message(call.message.chat.id, text='Ок')
            bot.send_message(call.message.chat.id, 'Введите название города (надёжнее на English)')
            bot.register_next_step_handler(call.message, weather)
        if call.data == "no":
            bot.send_message(call.message.chat.id, text="Чао! Когда вернетесь нажмите /start")


@bot.message_handler(content_types=['text'])
def weather(message):
    bot.send_message(message.chat.id, get_weather(message.text))
    markup = types.InlineKeyboardMarkup()
    item5 = types.InlineKeyboardButton("Да", callback_data="yes")
    item6 = types.InlineKeyboardButton("Нет", callback_data="no")
    markup.add(item5, item6)
    bot.send_message(message.chat.id, text='Продолжаем?', reply_markup=markup)


@bot.message_handler(content_types=['photo'])
def get_user_photo(message):
    bot.send_message(message.chat.id, 'Ну вроде ничё так')

bot.polling()

