# -*- coding: utf-8 -*-
import pyowm
import os
import telebot
from bs4 import BeautifulSoup
from requests import get
import datetime
from datetime import datetime
import pendulum
from flask import Flask, request
from telebot import types

TOKEN = '872790813:AAEvC64G7mZhNFbmBUOmc-hYvqhTpM56pw0'
bot = telebot.TeleBot(token=TOKEN)
server = Flask(__name__)


def temp():
    api = pyowm.OWM('9742b30206ebcadb2a29fa96eea64442')
    data = api.weather_at_place("Saint Petersburg,ru")
    weather = data.get_weather()
    temperature = weather.get_temperature('celsius')
    clouds = weather.get_clouds()
    t = str(temperature.get('temp')) + '°C'
    wind = weather.get_wind()

    if 0 <= clouds <= 5:
        str_weather = 'Сейчас ' + t + ' Безоблачно ' + str(wind.get('speed')) + 'm/s'
    else:
        str_weather = 'Сейчас ' + t + '\nОблачно ' + '\nВетер ' + str(wind.get('speed')) + 'm/s'
    return str_weather


def read_file(filename):
    with open(filename) as input_file:
        text = input_file.read()
    return text


def parser_data(filename):
    get_html()
    text = read_file(filename)
    soup = BeautifulSoup(text, 'html.parser')
    days = soup.find('table', {'class': ''})
    handle = open("text.txt", "w")
    handle.write(days.get_text())


def get_part(filename):
    timetable = open(filename).readlines()
    days = {0: 'ПН', 1: 'ВТ', 2: 'СР', 3: 'ЧТ', 4: 'ПТ', 5: 'СБ', 6: 'ВС'}
    date = datetime.today().strftime('%d.%m.%Y')
    weekday = datetime.today().weekday()
    today = date + days.get(weekday)
    tomorrow = pendulum.tomorrow('Europe/Moscow').format('DD.MM.20YY') + days.get(weekday + 1)
    count = 0

    with open(filename, 'w+') as output:
        for d in timetable:
            count += 1
            if d.strip() == today:
                other_days = timetable[count - 1:timetable.index(timetable[-1]):1]
                for i in other_days:
                    if i.strip() != tomorrow:
                        output.write(i)
                    else:
                        break


def get_part_tomorrow(filename):
    timetable = open(filename).readlines()
    days = {0: 'ПН', 1: 'ВТ', 2: 'СР', 3: 'ЧТ', 4: 'ПТ', 5: 'СБ', 6: 'ВС'}
    weekday = datetime.today().weekday()
    tomorrow = pendulum.tomorrow('Europe/Moscow').format('DD.MM.20YY') + days.get(weekday + 1)
    nextmorrow = pendulum.now('Europe/Moscow').add(days=2).format('DD.MM.20YY') + days.get(weekday + 2)
    count = 0

    with open(filename, 'w+') as output:
        for d in timetable:
            count += 1
            if d.strip() == tomorrow:
                other_days = timetable[count - 1:timetable.index(timetable[-1]):1]
                for i in other_days:
                    if i.strip() != nextmorrow:
                        output.write(i)
                    else:
                        break


def sorting(filename):
    strings = []
    lessons = {'09:00 - 10:35': 0, '10:50 - 12:25': 1, '12:40 - 14:15': 2, '14:30 - 16:00': 3}
    # добавить время пар, проверить если есть позже
    next_lessons = {0: '10:50 - 12:25', 1: '12:40 - 14:15', 2: '14:30 - 16:00', 3: '16:10 - 17:40'}
    lines_seen = set()
    lines_seen.add('\n')
    lines = open(filename).readlines()
    lines.remove(lines[0])
    first_lesson = lessons.get(lines[0].strip())
    next_lesson = next_lessons.get(first_lesson)
    t = 0

    for line in lines:
        if line not in lines_seen:
            if line.strip() != next_lesson:
                strings.append(line)
                lines_seen.add(line)
            else:
                strings.append('\n')
                lines_seen.clear()
                lines_seen.add('\n')
                lines_seen.add(line)
                strings.append(line)
                t += 1
                next_lesson = next_lessons.get(first_lesson + t)
    with open(filename, 'w+') as outfile:
        for line in strings:
            outfile.write(line)
    outfile.close()


def update_data():
    if os.stat('test.html').st_size != 0:
        parser_data('test.html')
        get_part('text.txt')
        sorting('text.txt')


def update_data_tomorrow():
    if os.stat('test.html').st_size != 0:
        parser_data('test.html')
        get_part_tomorrow('text.txt')
        sorting('text.txt')


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Приветствую', reply_markup=start_keyboard())


def start_keyboard():
    markup1 = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn1 = types.KeyboardButton('ИБ-1802')
    btn2 = types.KeyboardButton('ИБ-1801')
    btn3 = types.KeyboardButton('Э-1702')
    markup1.add(btn1, btn2, btn3)
    return markup1


def get_html(url):
    r = get(url)
    with open('test.html', 'w') as output_file:
        output_file.write(r.text)


@bot.message_handler(content_types=["text"])
def send_anytext(message):
    global texts
    chat_id = message.chat.id
    if message.text == 'На сегодня':
        update_data()
        texts = open('text.txt').read()
    if message.text == 'На завтра':
        update_data_tomorrow()
        texts = open('text.txt').read()
    if message.text == 'Погода☁':
        texts = temp()
    bot.send_message(chat_id, texts, reply_markup=keyboard())


@bot.message_handler(content_types=["text"])
def read_group(message):
    chat_id = message.chat.id
    if message.text == 'ИБ-1802':
        get_html('https://rasp.unecon.ru/raspisanie_grp.php?g=12244')
        bot.send_message(chat_id, 'понял вас', reply_markup=keyboard())
    if message.text == 'ИБ-1801':
        get_html('https://rasp.unecon.ru/raspisanie_grp.php?g=12057')
        bot.send_message(chat_id, 'понял вас', reply_markup=keyboard())
    if message.text == 'Э-1702':
        get_html('https://rasp.unecon.ru/raspisanie_grp.php?g=11808')
        bot.send_message(chat_id, 'понял вас', reply_markup=keyboard())


def keyboard():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn1 = types.KeyboardButton('На сегодня')
    btn2 = types.KeyboardButton('На завтра')
    btn3 = types.KeyboardButton('Погода☁')
    markup.add(btn1, btn2, btn3)
    return markup


@server.route('/' + TOKEN, methods=['POST'])
def get_message():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(
        url='https://polar-brushlands-12740.herokuapp.com/' + '872790813:AAEvC64G7mZhNFbmBUOmc-hYvqhTpM56pw0')
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
