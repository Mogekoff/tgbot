import telebot as tb
import logging
from decouple import config
import random
import os
from captcha.image import ImageCaptcha

logger = tb.logger
tb.logger.setLevel(logging.DEBUG)

TOKEN = config('BOT_TOKEN')
bot = tb.TeleBot(TOKEN)


def generateCaptcha():
    image = ImageCaptcha(width=280, height=90)
    captcha_text = str(random.randint(10**5, 10**6))
    data = image.generate(captcha_text)
    image.write(captcha_text, captcha_text)
    return captcha_text


@bot.message_handler(commands=['start', 'help'])
def auth(message):
    send_captcha(message)


def send_captcha(message=None):
    code = generateCaptcha()
    img = open(code, 'rb')
    bot.send_photo(message.chat.id, img, caption='Введите капчу с картинки:')
    img.close()
    os.remove(code)
    bot.register_next_step_handler(message, verify_captcha, code)

def verify_captcha(message, code, tries=0):
    tries += 1
    if message.text == code:
        bot.reply_to(message, 'Доступ разрешен!')
        start(message)
    elif tries > 2:
        bot.reply_to(message, f'Неверно. Все попытки исчерпаны. Повтор.')
        send_captcha(message)
    else:
        bot.reply_to(message, f'Неверно. Осталось попыток {3-tries}')
        bot.register_next_step_handler(message, verify_captcha, code, tries)


def start(message):
    bot.send_message(message.chat.id, "Добро пожаловать в моего бота епты")


@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)


bot.infinity_polling()