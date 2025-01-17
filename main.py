import telebot
from datetime import datetime
from telebot import types
import openpyxl
import os

#Создание временной директории для файлов
TEMP_DIR = 'temp_files'
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

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


@bot.message_handler(content_types='document')
def handle_file(message):
    chat_id = message.chat.id

    try:
        #Получение информации о файле
        file_id = message.document.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        #Сохранение файла во временную директорию
        file_name = message.document.file_name
        file_path = os.path.join(TEMP_DIR, file_name)
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        if file_name.endswith('.xlsx'):
            try:
                bot.reply_to(message, f'Файл успешно загружен, пожалуйста подождите...')

                #Открытие файла
                workbook = openpyxl.load_workbook(file_path)
                sheet = workbook.active


            except Exception as E:
                bot.reply_to(message, f'Ошибка при попытке открытия файла, {E}')
        else:
            bot.reply_to(message, 'Пожалуйста отправьте файл в формате "XLSX"')

        print('Файл принят!')

    except Exception as E:
        bot.reply_to(message, f'Произошла ошибка в работе бота, {E}')

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

print("Bot Started!")
bot.polling(non_stop=True)

