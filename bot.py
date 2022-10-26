import telebot
import sqlite3
#import parser_inst

from telebot import types
bot = telebot.TeleBot("5616283053:AAEBZ-buT-eA0xQiFvFFhLBqA5_ftkkUR4c")

data_admins = sqlite3.connect("admins.bd")
cursor_admins = data_admins.cursor()
users = [admin[0] for admin in cursor_admins.execute("""select distinct admin_chat_id from admins""").fetchall()]

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

        msg = bot.send_message(message.chat.id, "Введите ссылку на аккаунт и категорию, к которой он относится, через запятую", reply_markup=markup)
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

        item_1 = types.KeyboardButton("Категория 1")
        item_2 = types.KeyboardButton("Категория 2")
        back = types.KeyboardButton("Назад")
        markup.add(item_1, item_2, back)

        bot.send_message(message.chat.id, "Добавить категорию", reply_markup=markup)

    elif message.text == "Назад":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item_1 = types.KeyboardButton("Выбрать категорию")
        markup.add(item_1)

        bot.send_message(message.chat.id,
                         "Назад", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, message.text)

#functions add data

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
            if cat in [category[0] for category in cursor_categories.execute("""select distinct category_name from categories""").fetchall()]:
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
        if list_id_cat[i][1] == acc_data[1]:
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
#условие на out_message
#if message.text.lower() == "admin":
#    msg = bot.send_message(message.chat.id, "enter password")
#   bot.register_next_step_handler(msg, check_password)