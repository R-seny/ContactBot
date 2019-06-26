import telebot

bot = telebot.TeleBot()


@bot.message_handler(content_types=["text"])
def handle_text(message):
    print(message.text)
    if message.text == "Hi":
        bot.send_message(message.chat.id, "Hello! I am Bot. How can i help you?")
    else:
        bot.send_message(message.chat.id, "Sorry, i dont understand you.")


def listener(messages):
    """
    When new messages arrive TeleBot will call this function.
    """
    for m in messages:
        chatid = m.chat.id
        if m.content_type == 'text':
            text = m.text
            bot.send_message(chatid, text)
            bot.send_message(chatid, 'test')


bot.set_update_listener(listener) #register listener

bot.polling(none_stop=True, interval=0, timeout=20)

