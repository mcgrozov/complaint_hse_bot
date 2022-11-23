import os
os.system('pip install pyTelegramBotAPI')
import telebot
from telebot import types
bot = telebot.TeleBot('5447325606:AAHnzgoU2_3X6dmY8_UNVa7umyizaSpJtGw')
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,"""
Привет, я бот получения жалоб и комплиментов. 
Для доступа к функционалу необходима ргеистрация. 
Пожлауйста, введи команду: /reg
    """)
name = ''
surname = ''
faculty = ''
user_text = ''
@bot.message_handler(commands=['reg'])
def start(message):
    bot.send_message(message.from_user.id, 'Какое у тебя имя?')
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    global name
    name = message.text
    bot.send_message(message.from_user.id, 'Какая у тебя фамилия?')
    bot.register_next_step_handler(message, get_surname)

def get_surname(message):
    global surname
    surname = message.text
    bot.send_message(message.from_user.id,'С какого ты факультета?')
    bot.register_next_step_handler(message, get_faculty)

def get_faculty(message):
    global faculty
    faculty = message.text
    bot.send_message(message.chat.id,'Чтобы воспользоваться моими интсрументами введи /button')

def get_user_text(message):
    global user_text
    user_text = message.text
    bot.send_message(message.chat.id, 'Спасибо за обращение, я уже занимаюсь вашим вопросом')

@bot.message_handler(commands=['button'])
def buttons_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1= types.KeyboardButton("Хочу высказаться")
    markup.add(item1)
    item2 = types.KeyboardButton("Мне нужна красная кнопка")
    markup.add(item2)
    item3 = types.KeyboardButton("Рассмеши меня")
    markup.add(item3)
    bot.send_message(message.chat.id,'Выберите что вам надо',reply_markup=markup)
@bot.message_handler(content_types='text')
def messages_button_reply(message):
    if message.text=="Мне нужна красная кнопка":
        bot.send_message(message.chat.id,
                         "https://lk.hse.ru/user-suggestions?_gl=1%2a1jiumcf%2a_ga%2aMTcwMjg1MTU3MS4xNjY5MjMwNzc1%2a_ga_P5QXNNXGKL%2aMTY2OTIzMDc3NC4xLjEuMTY2OTIzMDc5NC40MC4wLjA.")
    elif message.text =="Рассмеши меня":
        bot.send_message(message.chat.id, """
— Может героин попробуем? Все лучше, чем Языковое разнообразие учить.
— А ты откуда знаешь? Учил, что ли?
        """)
    elif message.text =="Хочу высказаться":
        get_user_text(message)
bot.infinity_polling()