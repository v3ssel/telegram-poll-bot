import telebot

token = 'INSERT_TOKEN'
bot = telebot.TeleBot(token)


class BotHelper:
    y = -1
    x = -1
    nick = ''
    role = 0;
    question_id = 0
    question_number = 0
    question_step = 'showPoll'
