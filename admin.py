from basicui import *


@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text == 'Сменить аккаунт':
        start(message)
        return
    if (message.text == 'Создать голосование' or message.text == 'Управлять голосованиями' or message.text == 'Назад')\
            and BotHelper.nick != '':
        autorize(message, 0)
        return


def poll_answers(message):
    if message.text == 'Стоп':
        if BotHelper.y == 2:
            create_answer_list = """
                        INSERT INTO
                            answer_list (answer, question_id)
                        VALUES  ("%s", "%d")""" % ('Свой вариант', BotHelper.question_id)
            dal.execute_query(dal.connection, create_answer_list)
        bot.send_message(message.chat.id, 'Голосование успешно создано, '
                                          'его можно увидеть в пункте \'Управлять голосованиями\'')
        autorize(message, 0)
        return
    else:
        bot.register_next_step_handler(message, poll_answers)
    create_answer_list = """
            INSERT INTO
                answer_list (answer, question_id)
            VALUES  ("%s", "%d")""" % (message.text, BotHelper.question_id)
    dal.execute_query(dal.connection, create_answer_list)
    item = types.KeyboardButton('Стоп')
    mark = types.ReplyKeyboardMarkup(resize_keyboard=True)
    mark.add(item)
    bot.send_message(message.chat.id, 'А теперь пиши остальные ответы на вопрос, '
                                      'как закончишь нажми кнопку ниже', reply_markup=mark)
