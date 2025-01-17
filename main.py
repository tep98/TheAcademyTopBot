from os.path import split

import telebot
from datetime import datetime
from telebot import types
import openpyxl
import os

from telebot.apihelper import download_file
from telebot.storage import StateMemoryStorage

# Инициализация памяти для хранения состояний
storage = StateMemoryStorage()

#Создание временной директории для файлов
TEMP_DIR = 'temp_files'
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

TOKEN = ""
bot = telebot.TeleBot(TOKEN, state_storage=storage)

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

    #Создание кнопок для взаимодействия
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('1', callback_data='count_complited_classes'))
    markup.add(types.InlineKeyboardButton('2', callback_data='analyze_average_score'))

    #Отправка сообщения
    bot.send_message(message.chat.id, f"{welcome_word} {message.from_user.first_name}!\n\nВыберете действие:\n1. Подсчитывать количество проведенных пар по всем дисциплинам у группы\n2. Поиск студентов с средним баллом ниже чем 3", reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    chat_id = callback.message.chat.id

    if callback.data == 'count_complited_classes':
        bot.set_state(chat_id, "count_complited_classes")
        bot.send_message(chat_id, "Пришлите мне файл \"Расписание группы\" типа XLSX")
    elif callback.data == 'analyze_average_score':
        bot.set_state(chat_id, "analyze_average_score")
        bot.send_message(chat_id, "Пришлите мне файл \"Отчет по студентам\" типа XLSX")


@bot.message_handler(content_types='document')
def handle_file(message):
    chat_id = message.chat.id
    state = bot.get_state(chat_id)

    if not state:
        bot.send_message(chat_id, "Пожалуйста, выберите действие с помощью меню!")
        return

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

                #Действие 1 (Задание 7)
                if state == 'count_complited_classes':
                    rows_values = list(sheet.values)
                    print(rows_values)
                    subjects_list = []
                    subjects_count_list = []

                    #Логика для подсчета количества проведенных пар по всем дисциплинам
                    for row in rows_values[1:]:
                        for value in row[3:]:
                            if value is not None:
                                value_str = str(value)

                                if value_str.split(" ", 1)[0] == "Предмет:":
                                    value_str_splitline = value_str.splitlines()[0]

                                    if value_str_splitline not in subjects_list:
                                        subjects_list.append(value_str_splitline)
                                        subjects_count_list.append(1)

                                    else:
                                        index = subjects_list.index(value_str_splitline) if value_str_splitline in subjects_list else None
                                        if index is not None:
                                            if subjects_count_list[index] is not None:
                                                subjects_count_list[index] += 1

                    #Подсчет и вывод результатов
                    result = ""
                    for subject in range(len(subjects_list)):
                       result += f"{subjects_list[subject].split(' ', 1)[1]} - занятий: {subjects_count_list[subject]}\n"

                    if result == "":
                        bot.reply_to(message, "Файл не содержит требуемой информации, убедитесь в том, что выбрали нужный документ")
                        return

                    bot.send_message(chat_id, f"Группа: {sheet['A2'].value}\n\n{result}")



                #Действие 2 (Задание 5)
                elif state == 'analyze_average_score':

                    if not ("fio" in [cell.value.lower() for cell in sheet[1]]):
                        bot.reply_to(message, "Файл не содержит необходимых столбцов. Проверьте формат.")
                        return

                    first_row = tuple(sheet.rows)[0]

                    for cell in first_row:
                        print(cell.value)
                        match cell.value.lower():
                            case "fio":
                                FIO_cell = sheet[cell.column_letter]
                                continue
                            case "группа":
                                group_cell = sheet[cell.column_letter]
                                continue
                            case "homework":
                                HW_cell = sheet[cell.column_letter]
                                continue
                            case "classroom":
                                CW_cell = sheet[cell.column_letter]
                                continue
                        print("Значение не найдено")

                    bad_students_info = []
                    BORDER_MARK = 3

                    for cell in range(1, len(HW_cell)):
                        try:
                            avg_mark = (int(HW_cell[cell].value or 0) + int(CW_cell[cell].value or 0)) / 2
                        except ValueError:
                            bot.send_message(chat_id, f"Ошибка в данных ученика в строке {cell + 1}. Проверьте файл.")
                            continue

                        print(avg_mark)

                        if avg_mark < BORDER_MARK:
                            bad_student_info = FIO_cell[cell].value + " " + group_cell[cell].value + " - avg: " + str(avg_mark)
                            print(bad_student_info)
                            print("BAD")
                            bad_students_info.append(bad_student_info)
                        else:
                            print("GOOD")


                    result = ""
                    print(bad_students_info)
                    print("составление результата...")

                    for bad_student_info in bad_students_info:
                        result += bad_student_info + "\n"

                    print("Отправка результата...")

                    bot.send_message(message.chat.id, f"Студенты с баллом ниже чем {BORDER_MARK}:\n\n{result}")
                    print(bad_students_info)


            except Exception as E:
                bot.reply_to(message, f'Ошибка при попытке открытия файла, {E}')
        else:
            bot.reply_to(message, 'Пожалуйста отправьте файл в формате "XLSX"')

    except Exception as E:
        bot.reply_to(message, f'Произошла ошибка в работе бота, {E}')

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


print("Bot Started!")
bot.polling(non_stop=True)

