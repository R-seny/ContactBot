import telebot

bot = telebot.TeleBot("855197924:AAHkIDeoWI_nypSi7SBTjXy8YJMP2OSRv5Y")


@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text == "Hi":
        bot.send_message(message.from_user.id, "Hello! I am Bot. How can i help you?")
    else:
        bot.send_message(message.from_user.id, "Sorry, i dont understand you.")


bot.polling(none_stop=True, interval=0)
