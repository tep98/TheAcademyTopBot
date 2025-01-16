import telebot
from datetime import datetime


TOKEN = "7423667976:AAFzJ7_bb16iClqdOZzLMyualXT2vBp4hY8"
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

#Отправка сообщения
    bot.send_message(message.chat.id, f"{welcome_word} {message.from_user.first_name}!")


print("Bot Started!")
bot.polling(non_stop=True)

