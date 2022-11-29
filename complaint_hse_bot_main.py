# import os
# os.system('pip install pyTelegramBotAPI')

import random
import telebot
from telebot import types

bot = telebot.TeleBot('5447325606:AAHnzgoU2_3X6dmY8_UNVa7umyizaSpJtGw')

course = ''
faculty = ''
complaints = []


def memes_reader(path):
    with open(path, encoding='utf-8') as mf:
        memes = mf.readlines()
    return memes


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, """
Привет, я бот получения жалоб и комплиментов. 
Здесь ты можешь высказать свою жалобу или комлимент относительно учебы в НИУ ВШЭ НН.
Также мы можем предложить тебе психологическую поддержку ввиде мема:)
Введи команду /button""")


@bot.message_handler(commands=['button'])
def buttons_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Обратиться к вышке")
    markup.add(item1)
    item2 = types.KeyboardButton("Мне нужна красная кнопка")
    markup.add(item2)
    item3 = types.KeyboardButton("Рассмеши меня")
    markup.add(item3)
    bot.send_message(message.chat.id, 'Жми на одну из кнопок внизу ↓', reply_markup=markup)


def buttons_funny(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Хочу мем")
    markup.add(item1)
    item2 = types.KeyboardButton("Хочу цитату")
    markup.add(item2)
    bot.send_message(message.chat.id, 'Как я могу тебя рассмешить?', reply_markup=markup)


def buttons_more_funny(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Еще мем")
    markup.add(item1)
    item2 = types.KeyboardButton("Теперь цитату")
    markup.add(item2)
    item3 = types.KeyboardButton("Обратно в меню")
    markup.add(item3)
    bot.send_message(message.chat.id, 'Что-нибудь еще?', reply_markup=markup)
    bot.register_next_step_handler(message, send_meme)


def buttons_more_cites(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Еще цитату")
    markup.add(item1)
    item2 = types.KeyboardButton("Теперь мем")
    markup.add(item2)
    item3 = types.KeyboardButton("Обратно в меню")
    markup.add(item3)
    bot.send_message(message.chat.id, 'Что-нибудь еще?', reply_markup=markup)
    bot.register_next_step_handler(message, send_meme)


@bot.message_handler(func=lambda msg: msg.text in ["Мне нужна красная кнопка", "Рассмеши меня", "Обратиться к вышке"])
def messages_button_reply(message):
    # красную кнопку в отдельную функцию
    if message.text == "Мне нужна красная кнопка":
        bot.send_message(message.chat.id,
                         "https://lk.hse.ru/user-suggestions?_gl=1%2a1jiumcf%2a_ga%2aMTcwMjg1MTU3MS4xNjY5MjMwNzc1%2a_ga_P5QXNNXGKL%2aMTY2OTIzMDc3NC4xLjEuMTY2OTIzMDc5NC40MC4wLjA.")

    elif message.text == "Рассмеши меня":
        buttons_funny(message)
        bot.register_next_step_handler(message, send_meme)

    elif message.text == "Обратиться к вышке":
        bot.send_message(message.chat.id, 'Опиши свою проблему', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_complaint)


def send_meme(message):
    global memes

    if message.text in ['Хочу мем', 'Еще мем', 'Теперь мем']:
        bot.send_photo(message.chat.id, random.choice(memes))
        buttons_more_funny(message)

    elif message.text in ['Хочу цитату', 'Еще цитату', 'Теперь цитату']:
        bot.send_message(message.chat.id, """
        — Может героин попробуем? Все лучше, чем Языковое разнообразие учить.
    — А ты откуда знаешь? Учил, что ли?""")
        buttons_more_cites(message)

    elif message.text == 'Обратно в меню':
        buttons_message(message)


def get_complaint(message):
    global complaints
    complaints.append(message.text)
    bot.send_message(message.chat.id, 'Чтобы завершить регестрацию проблемы, напиши, пожалуйста, на каком направлении ты учишься')
    bot.register_next_step_handler(message, get_faculty)


def get_faculty(message):
    global faculty
    faculty = message.text
    bot.send_message(message.chat.id, 'На каком курсе ты обучаешься? (Для магистратуры введи, пожалуйста, 5 или 6 соответственно)')
    bot.register_next_step_handler(message, get_course)


def get_course(message):
    global course
    course = message.text
    bot.send_message(message.chat.id, 'Спасибо, твоя жалоба записана!')
    buttons_message(message)


@bot.message_handler(content_types=['text'])
def echo(message):
    bot.send_message(message.chat.id, message.text)


def get_user_text(message):
    global user_text
    user_text = message.text
    bot.send_message(message.chat.id, 'Спасибо за обращение, я уже занимаюсь вашим вопросом')


if __name__ == '__main__':
    memes = memes_reader('memes.txt')
    bot.infinity_polling()
