import telebot
from datetime import datetime
from telebot import types


TOKEN = ""
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'restart'])
def start(message):

    #Вычисление текущего времени суток
    current_time = int(datetime.now().strftime("%H"))
    welcome_word = 'Добрый день'
    if (current_time>=18) and (current_time < 24):
        welcome_word = 'Добрый вечер'
    elif (current_time>=0) and (current_time < 6):
        welcome_word = 'Доброй ночи'
    elif (current_time>=6) and (current_time < 12):
        welcome_word = 'Доброе утро'

        # Создание кнопок для взаимодействия
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('1', callback_data='count_complited_classes'))
    markup.add(types.InlineKeyboardButton('2', callback_data='analyze_average_score'))

    # Отправка сообщения
    bot.send_message(message.chat.id, f"{welcome_word} {message.from_user.first_name}!\n\nВыберете действие:\n1. Подсчитывать количество проведенных пар по всем дисциплинам у группы\n2. Поиск студентов с средним баллом ниже чем 3", reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    chat_id = callback.message.chat.id

    if callback.data == 'count_complited_classes':
        bot.send_message(chat_id, "Пришлите мне файл \"Расписание группы\" типа XLSX")
    elif callback.data == 'analyze_average_score':
        bot.send_message(chat_id, "Пришлите мне файл \"Отчет по студентам\" типа XLSX")

print("Bot Started!")
bot.polling(non_stop=True)

