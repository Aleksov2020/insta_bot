import telebot
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler
from tzlocal import get_localzone
tz = get_localzone()

# 637989615

from telebot import types

bot = telebot.TeleBot("5616283053:AAEBZ-buT-eA0xQiFvFFhLBqA5_ftkkUR4c")

data_admins = sqlite3.connect("admins.bd")
cursor_admins = data_admins.cursor()
#users = [admin[0] for admin in cursor_admins.execute("""select distinct admin_chat_id from admins""").fetchall()]
users = [1,2]

def parsing_accounts():
    # выгружаем категории и их id из таблицы
    data_categories = sqlite3.connect('categories.bd')
    cursor_categories = data_categories.cursor()
    list_cat = [cat for cat in
                cursor_categories.execute("""select category_id, category_name from categories""").fetchall()]

    # выгружаем аккаунты и id категорий, к которым они относятся
    data_accounts = sqlite3.connect('accounts.bd')
    cursor_accounts = data_accounts.cursor()
    list_acc = [acc for acc in cursor_accounts.execute("""select link, category_id from accounts""").fetchall()]

    # выгружаем id пользователей и выбранная ими категория

    # data_users = sqlite3.connect('users.bd')
    # cursor_users = data_users.cursor()
    # list_users = [user for user in cursor_users.execute("""select user_id, category_id from accounts""").fetchall()]

    list_users = [(637989615, 2)]

    for cat in list_cat:
        for acc in list_acc:
            if cat[0] == acc[1]:
                for user in list_users:
                    if user[1] == cat[0]:
                        # передаем аккаунт в функцию парсинга
                        bot.send_message(user[0], "str(acc[1])")

sched = BackgroundScheduler(timezone=tz)
sched.add_job(parsing_accounts,'cron', hour= 13, minute = '47')
sched.start()


@bot.message_handler(func=lambda message: message.chat.id in users, commands=['start'])
def admin_welcome_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    item_1 = types.KeyboardButton("Добавить категории")
    item_2 = types.KeyboardButton("Статистика сообщений")
    item_3 = types.KeyboardButton("Добавить аккаунт к категории")
    item_4 = types.KeyboardButton("Добавить администратора")

    markup.add(item_1, item_2, item_3, item_4)
    bot.send_message(message.chat.id, 'Привет, администратор!', reply_markup=markup)


@bot.message_handler(func=lambda message: message.chat.id in users, content_types=['text'])
def admin_out_message(message):
    if message.text == "Добавить категории" or message.text == "Добавить еще категории":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item_1 = types.KeyboardButton("Добавить еще категории")
        back = types.KeyboardButton("Назад")
        markup.add(item_1, back)

        msg = bot.send_message(message.chat.id, "Введите новые категории через запятую", reply_markup=markup)
        bot.register_next_step_handler(msg, add_categories)

    elif message.text == "Добавить администратора" or message.text == "Добавить еще администратора":

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item_1 = types.KeyboardButton("Добавить еще администратора")
        back = types.KeyboardButton("Назад")
        markup.add(item_1, back)

        msg = bot.send_message(message.chat.id, "Введите id пользователя", reply_markup=markup)
        bot.register_next_step_handler(msg, add_admins)

    elif message.text == "Добавить аккаунт к категории" or message.text == "Добавить еще аккаунт":

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item_1 = types.KeyboardButton("Добавить еще аккаунт")
        back = types.KeyboardButton("Назад")
        markup.add(item_1, back)

        msg = bot.send_message(message.chat.id,
                               "Введите ссылку на аккаунт и категорию, к которой он относится, через запятую",
                               reply_markup=markup)
        bot.register_next_step_handler(msg, add_accounts)
    elif message.text == "Назад":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item_1 = types.KeyboardButton("Добавить категории")
        item_2 = types.KeyboardButton("Статистика сообщений")
        item_3 = types.KeyboardButton("Добавить аккаунт к категории")
        item_4 = types.KeyboardButton("Добавить администратора")

        markup.add(item_1, item_2, item_3, item_4)

        bot.send_message(message.chat.id,
                         "Назад", reply_markup=markup)

    elif message.text == "bot_hui":
        parsing_accounts()

    elif message.text == "start_bot" or message.text == "stop_bot":
        while True:
            bot.send_message(
                message.chat.id,
                "Список ссылочек: ")

            if message.text == "stop_bot":
                break
    else:
        bot.send_message(message.chat.id, message.text)


@bot.message_handler(func=lambda message: message.chat.id not in users, commands=['start'])
def user_welcome_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_1 = types.KeyboardButton("Выбрать категорию")
    markup.add(item_1)
    bot.send_message(message.chat.id,
                     "Hello, {0.first_name}!\nI am <b>{1.first_name}</b>".format(message.from_user, bot.get_me()),
                     parse_mode="html", reply_markup=markup)




@bot.message_handler(func=lambda message: message.chat.id not in users, content_types=['text'])
def user_out_message(message):
    if message.text == "Выбрать категорию":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Назад"))
        data_categories = sqlite3.connect('categories.bd')
        cursor_categories = data_categories.cursor()
        list_cat = [cat for cat in
                    cursor_categories.execute("""select category_id, category_name from categories""").fetchall()]

        for category in list_cat:
            markup.add(types.KeyboardButton(category[1]))

        msg = bot.send_message(message.chat.id, "Выберете категорию", reply_markup=markup)
        bot.register_next_step_handler(msg, add_users_categories)


    elif message.text == "Назад":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item_1 = types.KeyboardButton("Выбрать категорию")
        markup.add(item_1)

        bot.send_message(message.chat.id,
                         "Назад", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, message.text)


# functions add data

def add_users_categories(message):
    if message.text == "Назад":
        user_out_message(message)
    else:
        data_users = sqlite3.connect('users.bd')
        cursor_users = data_users.cursor()
        cursor_users.execute("""
            CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY AUTOINCREMENT, user_chat_id INTEGER, category_id INTEGER
             );""")
        data_categories = sqlite3.connect('categories.bd')
        cursor_categories = data_categories.cursor()
        list_cat = [cat[0] for cat in
                    cursor_categories.execute("""select distinct category_name from categories""").fetchall()]
        list_cat_for = [cat for cat in
                    cursor_categories.execute("""select category_id, category_name from categories""").fetchall()]

        if message.text in list_cat:
            cat_id = 0
            for cat in list_cat_for:
                if message.text == cat[1]:
                    cat_id = cat[0]
            cursor_users.execute("INSERT INTO users (user_chat_id, category_id) VALUES(?,?);", [message.chat.id, cat_id])
            data_users.commit()
            bot.send_message(message.chat.id, "Категория добавлена!")
        else:
            msg = bot.send_message(message.chat.id, "Такой категории нет!")
            bot.register_next_step_handler(msg, add_users_categories)


def add_categories(message):
    list_cat = str(message.text).split(", ")

    data_categories = sqlite3.connect('categories.bd')
    cursor_categories = data_categories.cursor()
    cursor_categories.execute("""
    CREATE TABLE IF NOT EXISTS categories(
    category_id INTEGER PRIMARY KEY AUTOINCREMENT, category_name STRING
     );""")

    for cat in list_cat:
        try:
            if cat in [category[0] for category in
                       cursor_categories.execute("""select distinct category_name from categories""").fetchall()]:
                bot.send_message(message.chat.id, f"Категория {cat} уже существует!")
            else:
                cursor_categories.execute("INSERT INTO categories (category_name) VALUES(?);", [cat.lower()])
                data_categories.commit()
                bot.send_message(message.chat.id, "Категории добавлены")
        except:
            bot.send_message(message.chat.id, "Данные введены некорректно!")


def add_admins(message):
    data_admins = sqlite3.connect("admins.bd")
    cursor_admins = data_admins.cursor()
    cursor_admins.execute("""
    CREATE TABLE IF NOT EXISTS admins(
    admin_id INTEGER PRIMARY KEY AUTOINCREMENT, admin_chat_id INTEGER
     );""")
    cursor_admins.execute("INSERT INTO admins (admin_chat_id) VALUES(?);", [int(message.text)])
    data_admins.commit()
    bot.send_message(message.chat.id, "Администратор добавлен!")


def add_accounts(message):
    acc_data = str(message.text).split(", ")

    data_accounts = sqlite3.connect('accounts.bd')
    cursor_accounts = data_accounts.cursor()
    cursor_accounts.execute("""CREATE TABLE IF NOT EXISTS accounts(
    account_id INTEGER PRIMARY KEY AUTOINCREMENT, link STRING, category_id INTEGER
     );""")

    data_categories = sqlite3.connect('categories.bd')
    cursor_categories = data_categories.cursor()

    list_id_cat = cursor_categories.execute("""select distinct category_id, category_name from categories""").fetchall()
    cat_id = -5
    for i in range(len(list_id_cat)):
        if list_id_cat[i][1] == acc_data[1].lower():
            cat_id = list_id_cat[i][0]
    if cat_id == -5:
        bot.send_message(message.chat.id, "Такая категория не добавлена!")
    else:
        cursor_accounts.execute("INSERT INTO accounts (link, category_id) VALUES(?,?);", [acc_data[0], cat_id])
        data_accounts.commit()
        bot.send_message(message.chat.id, "Аккаунт добавлен!")


bot.polling(none_stop=True)

# def check_password(message):
#    if message.text == "1":
#       bot.send_message(message.chat.id, "Hello, admin!")
#    else:
#        ms = bot.send_message(message.chat.id, "Invalid password")
#       bot.register_next_step_handler(ms, check_password)
# условие на out_message
# if message.text.lower() == "admin":
#    msg = bot.send_message(message.chat.id, "enter password")
#   bot.register_next_step_handler(msg, check_password)
