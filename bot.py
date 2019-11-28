# -*- coding: utf-8 -*-
import os

import telebot
from bs4 import BeautifulSoup
from requests import get
import datetime
from datetime import datetime
import pendulum
from flask import Flask, request

TOKEN = '872790813:AAEvC64G7mZhNFbmBUOmc-hYvqhTpM56pw0'
bot = telebot.TeleBot(token=TOKEN)
server = Flask(__name__)


def read_file(filename):
    with open(filename) as input_file:
        text = input_file.read()
    return text


def get_html():
    url = 'https://rasp.unecon.ru/raspisanie_grp.php?searched=1&g=12244'  # url
    r = get(url)
    with open('test.html', 'w') as output_file:
        output_file.write(r.text)


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

    with open('test.txt', 'w') as output:
        for d in timetable:
            count += 1
            if d.strip() == today:
                other_days = timetable[count - 1:timetable.index(timetable[-1]):1]
                for i in other_days:
                    if i.strip() != tomorrow:
                        output.write(i)
                    else:
                        break


def sorting(filename):
    # time_lessons = {1: '09:00 - 10:35', 2: '10:50 - 12:25',
    #                 3: '12:40 - 14:15', 4: '14:30 - 16:00', 5: '16:10 - 17:40'}
    lessons = {'09:00 - 10:35', '10:50 - 12:25', '12:40 - 14:15',
               '14:30 - 16:00', '16:10 - 17:40'}
    strings = []
    lines_seen = set()  # holds lines already seen
    lines = open(filename).readlines()
    for line in reversed(lines):
        if line not in lines_seen:  # not a duplicate
            strings.append(line)
            lines_seen.add(line)
    with open(filename, 'w+') as outfile:
        for line in reversed(strings):
            outfile.write(line)
    outfile.close()


# полная жопа надо переформить

def update_data():
    get_html()
    if os.stat('test.html').st_size != 0:
        parser_data('test.html')
        get_part('text.txt')
        sorting('test.txt')


def find_at(msg):
    for text in msg:
        if 'timetable' in text:
            return text


@bot.message_handler(commands=['start'])
def send_welcome(message):
    update_data()
    bot.reply_to(message, 'Welcome')


@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.reply_to(message, 'To use this bot, send word timetable')


@bot.message_handler(func=lambda msg: msg.text is not None and 'timetable' in msg.text)
def at_answer(message):
    texts = message.text.split()
    at_text = find_at(texts)
    doc = open('message.txt').read()
    bot.reply_to(message, doc)


@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
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
