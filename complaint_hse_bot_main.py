import random
from collections import defaultdict

import pandas as pd
import telebot
from sqlalchemy import Table, Column, String, MetaData, insert, text
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from telebot import types


engine = create_engine('sqlite:///complaint.db', echo=True, future=True)
meta = MetaData()
if not database_exists(engine.url):
    create_database(engine.url)

complaints = Table(
   'complaints', meta,
   Column('faculty', String),
   Column('year', String),
   Column('complaint', String),
)

users = Table(
    'users', meta,
    Column('chat_id', String),
    Column('faculty', String),
    Column('specialisation', String),
    Column('year', String),
)

meta.create_all(engine)

bot = telebot.TeleBot('5447325606:AAHnzgoU2_3X6dmY8_UNVa7umyizaSpJtGw')

info_by_chat_id = defaultdict(defaultdict)


def buttons_funny(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Хочу мем"))
    markup.add(types.KeyboardButton("Хочу цитату"))
    bot.send_message(message.chat.id, "Как я могу тебя рассмешить?", reply_markup=markup)


@bot.message_handler(commands=['button'])
def buttons_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Обратиться к Вышке"))
    markup.add(types.KeyboardButton("Мне нужна красная кнопка"))
    markup.add(types.KeyboardButton("Рассмеши меня"))
    markup.add(types.KeyboardButton("Личная помощь"))
    bot.send_message(message.chat.id, "Жми на одну из кнопок внизу ↓", reply_markup=markup)


def buttons_more_cites(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Еще цитату"))
    markup.add(types.KeyboardButton("Теперь мем"))
    markup.add(types.KeyboardButton("Обратно в меню"))
    bot.send_message(message.chat.id, "Что-нибудь еще?", reply_markup=markup)
    bot.register_next_step_handler(message, send_more)


def buttons_more_funny(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Еще мем"))
    markup.add(types.KeyboardButton("Теперь цитату"))
    markup.add(types.KeyboardButton("Обратно в меню"))
    bot.send_message(message.chat.id, "Что-нибудь еще?", reply_markup=markup)
    bot.register_next_step_handler(message, send_more)


def buttons_more_help(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Хочу получить другую информацию"))
    markup.add(types.KeyboardButton("Обратно в меню"))
    bot.send_message(message.chat.id, "Что-нибудь еще?", reply_markup=markup)
    bot.register_next_step_handler(message, help_type)


def buttons_red_button(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Мне все еще нужна кнопка")
    markup.add(item1)
    item2 = types.KeyboardButton("Обратно в меню")
    markup.add(item2)

    text = "Красная (или Выразительная) кнопка - это форма обращения к Управлению по организации процесса обучения. " \
           "Ваша жалоба поступит напрямую в Управление, которое занимается организацией процесса обучения ВШЭ. " \
           "Претензия будет передана в подразделение, компетенцией которого является решение указанной проблемы.\n\n" \
           "Не рекомендуем использовать Выразительную кнопку, если есть возможность решить проблему иными способами: " \
           "вы можете обратиться к академическому руководителю, в свой деканат или оставить жалобу в этом боте!\n\n" \
           "Хотите продолжить?"

    bot.send_message(message.chat.id, text, reply_markup=markup)
    bot.register_next_step_handler(message, buttons_red_final)


def buttons_red_final(message):
    if message.text == 'Мне все еще нужна кнопка':
        bot.send_message(
            message.chat.id,
            "[Ссылка на красную кнопку]"
            "(https://lk.hse.ru/user-suggestions?_gl=1%2a1jiumcf%2a_ga%2aMTcwMjg1MTU3MS4xNjY5MjMwNzc1%2a_"
            "ga_P5QXNNXGKL%2aMTY2OTIzMDc3NC4xLjEuMTY2OTIzMDc5NC40MC4wLjA.)",
            parse_mode="MarkdownV2"
        )
    buttons_message(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "cb_like":
        # open the memes file and add link once again
        bot.answer_callback_query(call.id, "Рад, что понравилось!")
    elif call.data == "cb_dislike":
        bot.answer_callback_query(call.id, "Спасибо за отзыв, учтем!")


def done_complaint(message):
    insertion = insert(complaints).values(
        complaint=info_by_chat_id[message.chat.id]['complaint'],
        faculty=info_by_chat_id[message.chat.id]['faculty'],
        year=info_by_chat_id[message.chat.id]['year']
    )
    with engine.connect() as conn:
        conn.execute(insertion)
        conn.commit()
    bot.send_message(message.chat.id, "Спасибо, твоя жалоба записана!")
    buttons_message(message)


@bot.callback_query_handler(func=lambda call: True)
def faculty_handler(message):
    msg = message.text

    if msg == "Факультет гуманитарных наук":
        info_by_chat_id[message.chat.id]['faculty'] = msg
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Филология"), types.KeyboardButton("Дизайн"))
        markup.add(types.KeyboardButton("Фундаментальная и прикладная лингвистика"))
        markup.add(types.KeyboardButton("Иностранные языки и межкультурная бизнес-коммуникация"))
        markup.add(types.KeyboardButton("Прикладная лингвистика и текстовая аналитика"))
        markup.add(types.KeyboardButton("Современные филологические практики: поэтика, интерпретация, комментарий"))
        bot.reply_to(
            message=message,
            text='Теперь выбери свою ОП',
            reply_markup=markup
        )
        bot.register_next_step_handler(message, faculty_handler)
    elif msg == "Факультет права":
        info_by_chat_id[message.chat.id]['faculty'] = msg
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Юриспруденция"))
        markup.add(types.KeyboardButton("Правовое обеспечение и защита бизнеса"))
        bot.reply_to(
            message=message,
            text='Теперь выбери свою ОП',
            reply_markup=markup
        )
        bot.register_next_step_handler(message, faculty_handler)
    elif msg == "Факультет менеджмента":
        info_by_chat_id[message.chat.id]['faculty'] = msg
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Управление бизнесом"), types.KeyboardButton("Цифровой маркетинг"))
        markup.add(types.KeyboardButton("Организация и управление предприятием"))
        markup.add(types.KeyboardButton("Международный бакалавриат по бизнесу и экономике"))
        markup.add(types.KeyboardButton("Управление развитием компании"), types.KeyboardButton("Управление образованием"))
        markup.add(types.KeyboardButton("Управление бизнесом в глобальных условиях"), types.KeyboardButton("Маркетинг"))
        markup.add(types.KeyboardButton("Управление организациями и проектами"))
        bot.reply_to(
            message=message,
            text='Теперь выбери свою ОП',
            reply_markup=markup
        )
        bot.register_next_step_handler(message, faculty_handler)
    elif msg == "Факультет экономики":
        info_by_chat_id[message.chat.id]['faculty'] = msg
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Экономика"), types.KeyboardButton("Международный бакалавриат по бизнесу и экономике"))
        markup.add(types.KeyboardButton("Экономика и бизнес"), types.KeyboardButton("Экономика и анализ бизнеса"))
        markup.add(types.KeyboardButton("Финансы"), types.KeyboardButton("Бизнес-аналитика в экономике и менеджменте"))
        bot.reply_to(
            message=message,
            text='Теперь выбери свою ОП',
            reply_markup=markup
        )
        bot.register_next_step_handler(message, faculty_handler)
    elif msg == "Факультет информатики, математики и компьютерных наук":
        info_by_chat_id[message.chat.id]['faculty'] = msg
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Компьютерные науки и технологии"), types.KeyboardButton("Программная инженерия"))
        markup.add(types.KeyboardButton("Прикладная математика и информатика"), types.KeyboardButton("Математика (бакалавриат)"))
        markup.add(types.KeyboardButton("Интеллектуальный анализ данных"), types.KeyboardButton("Бизнес-информатика"))
        markup.add(types.KeyboardButton("Магистр по компьютерному зрению"), types.KeyboardButton("Математика (магистратура)"))
        bot.reply_to(
            message=message,
            text='Теперь выбери свою ОП',
            reply_markup=markup
        )
        bot.register_next_step_handler(message, faculty_handler)
    elif msg in [str(i) for i in range(1, 5)]:
        info_by_chat_id[message.chat.id]['year'] = msg
        insertion = insert(users).values(
            chat_id=message.chat.id,
            faculty=info_by_chat_id[message.chat.id]['faculty'],
            specialisation=info_by_chat_id[message.chat.id]['specialisation'],
            year=info_by_chat_id[message.chat.id]['year']
        )
        with engine.connect() as conn:
            conn.execute(insertion)
            conn.commit()

        if info_by_chat_id[message.chat.id]['action'] == 'help':
            bot.register_next_step_handler(message, help_type)
        elif info_by_chat_id[message.chat.id]['action'] == 'complaint':
            bot.register_next_step_handler(message, done_complaint)
    else:
        info_by_chat_id[message.chat.id]['specialisation'] = msg
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=6)
        for i in range(1, 5):
            markup.add(types.KeyboardButton(str(i)))
        bot.reply_to(
            message=message,
            text='Теперь выбери свой курс',
            reply_markup=markup
        )
        bot.register_next_step_handler(message, faculty_handler)


def faculty_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Факультет гуманитарных наук"), types.KeyboardButton("Факультет права"))
    markup.add(types.KeyboardButton("Факультет менеджмента"), types.KeyboardButton("Факультет экономики"))
    markup.add(types.KeyboardButton("Факультет информатики, математики и компьютерных наук"))
    return markup


# @bot.message_handler(content_types=["text"])
# def echo(message):
#     bot.send_message(message.chat.id, message.text)


def gen_markup():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        types.InlineKeyboardButton("👍", callback_data="cb_like"),
        types.InlineKeyboardButton("👎", callback_data="cb_dislike")
    )
    return markup


def get_complaint(message):
    info_by_chat_id[message.chat.id]['complaint'] = message.text
    with engine.connect() as conn:
        res = conn.execute(text(f'select * from users where chat_id = {message.chat.id}')).fetchall()
    if res:
        print(res)
        info_by_chat_id[message.chat.id]['faculty'] = res[0][1]
        info_by_chat_id[message.chat.id]['specialisation'] = res[0][2]
        info_by_chat_id[message.chat.id]['year'] = res[0][3]
        done_complaint(message)
    else:
        bot.send_message(
            message.chat.id,
            "Чтобы завершить регистрацию проблемы, выбери свой факультет",
            reply_markup=faculty_markup()
        )
        info_by_chat_id[message.chat.id]['action'] = 'complaint'
        bot.register_next_step_handler(message, faculty_handler)


@bot.callback_query_handler(func=lambda call: True)
def help_handler(message):
    def separate_values(values):
        return "\n".join(values.item().split(', '))

    global mails
    info = mails[mails["Направление"] == info_by_chat_id[message.chat.id]["specialisation"]]
    if info.empty:
        bot.send_message(message.chat.id, "К сожалению, твоей ОП еще нет в списке")
        buttons_more_help(message)

    if message.text == "Помощь деканата":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Номер менеджера ОП"))
        markup.add(types.KeyboardButton("Почта менеджера ОП"))
        markup.add(types.KeyboardButton("Время работы деканата"))
        markup.add(types.KeyboardButton("Обратно в меню"))
        bot.reply_to(
            message=message,
            text="Выбери способ связи",
            reply_markup=markup
        )
        bot.register_next_step_handler(message, help_handler)

    elif message.text == "Помощь академического руководителя":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Почта академического руководителя"))
        markup.add(types.KeyboardButton("Обратно в меню"))
        bot.reply_to(
            message=message,
            text="Выбери способ связи",
            reply_markup=markup
        )
        bot.register_next_step_handler(message, help_handler)

    elif message.text == "Номер менеджера ОП":
        bot.reply_to(
            message=message,
            text=f'{separate_values(info["ФИО менеджера ОП"])}\n'
                 f'{separate_values(info["Номер менеджера ОП"])}'
        )
        buttons_more_help(message)
    elif message.text == "Почта менеджера ОП":
        bot.reply_to(
            message=message,
            text=f'{separate_values(info["ФИО менеджера ОП"])}\n'
                 f'{separate_values(info["Почта менеджера ОП"])}'
        )
        buttons_more_help(message)
    elif message.text == "Время работы деканата":
        bot.reply_to(
            message=message,
            text=f'{separate_values(info["ФИО менеджера ОП"])}\n'
                 f'{separate_values(info["Время работы деканата"])}'
        )
        buttons_more_help(message)

    elif message.text == "Почта академического руководителя":
        bot.reply_to(
            message=message,
            text=f'{separate_values(info["ФИО академичеcкого руководителя"].values)}\n'
                 f'{separate_values(info["Почта академического руководителя"].values)}'
        )
        buttons_more_help(message)

    elif message.text == "Обратно в меню":
        buttons_message(message)


def help_type(message):
    if message.text == 'Обратно в меню':
        buttons_message(message)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Помощь деканата"))
    markup.add(types.KeyboardButton("Помощь академического руководителя"))
    markup.add(types.KeyboardButton("Обратно в меню"))
    bot.send_message(message.chat.id, "Чья помощь тебе необходима?", reply_markup=markup)
    bot.register_next_step_handler(message, help_handler)


def memes_reader(path):
    with open(path, encoding='utf-8') as mf:
        memes = mf.readlines()
    return memes


@bot.message_handler(func=lambda msg: msg.text in (
        "Мне нужна красная кнопка", "Рассмеши меня", "Личная помощь", "Обратиться к Вышке"
))
def messages_button_reply(message):
    # красную кнопку в отдельную функцию
    if message.text == "Мне нужна красная кнопка":
        buttons_red_button(message)

    elif message.text == "Рассмеши меня":
        buttons_funny(message)
        bot.register_next_step_handler(message, send_more)

    elif message.text == "Обратиться к Вышке":
        bot.send_message(message.chat.id, "Опиши свою проблему", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_complaint)

    elif message.text == "Личная помощь":
        with engine.connect() as conn:
            res = conn.execute(text(f'select * from users where chat_id = {message.chat.id}')).fetchall()
        if res:
            print(res)
            info_by_chat_id[message.chat.id]['specialisation'] = res[0][2]
            help_type(message)
        else:
            bot.send_message(
                message.chat.id,
                "Выбери свой факультет",
                reply_markup=faculty_markup()
            )
            info_by_chat_id[message.chat.id]['action'] = 'help'
            bot.register_next_step_handler(message, faculty_handler)


def send_more(message):
    global memes

    if message.text in ["Хочу мем", "Еще мем", "Теперь мем"]:
        bot.send_photo(message.chat.id, random.choice(memes), reply_markup=gen_markup())
        buttons_more_funny(message)

    elif message.text in ["Хочу цитату", "Еще цитату", "Теперь цитату"]:
        bot.send_message(
            message.chat.id,
            random.choice(jokes),
            reply_markup=gen_markup()
        )
        buttons_more_cites(message)

    elif message.text == "Обратно в меню":
        buttons_message(message)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(
        message.chat.id,
        "Привет, я бот получения жалоб и комплиментов.\n"
        "Здесь ты можешь высказать свою жалобу или комплимент относительно учебы в НИУ ВШЭ НН.\n"
        "Также мы можем предложить тебе психологическую поддержку в виде мема:)\n"
        "Введи команду /button"
    )


if __name__ == "__main__":
    memes = memes_reader("memes.txt")
    mails = pd.read_csv('mails.csv')
    jokes = pd.read_csv('jokes.csv')['joke'].to_list()
    bot.infinity_polling()
