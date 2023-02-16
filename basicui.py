import base64
import dal
from telebot import types
from kernel import (BotHelper, bot)


def is_base64(sb):
    try:
        if isinstance(sb, str):
            sb_bytes = bytes(sb, 'ascii')
        elif isinstance(sb, bytes):
            sb_bytes = sb
        else:
            raise ValueError("Argument must be string or bytes")
        a = str(base64.b85encode(base64.b85decode(sb_bytes)).decode("utf-8"))
        if len(a) < len(sb):
            sb = a[:len(sb)]
        else:
            a = a[:-1]
            sb = sb[:-1]
        return str(a) == str(sb)
    except Exception:
        return False


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, 'Привет, тут ты можешь создать или голосовать в опросах Школы 21.\n'
                                      'Но для начала авторизуйся. Просто напиши свой логин интры/платформы')
    bot.register_next_step_handler(message, autorize, 1)


def autorize(message, flag):
    mark = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    check_name = -1
    if flag == 1:
        BotHelper.nick = message.text
        check_name = valid_name(message)
    if flag == 0 and BotHelper.role == 'admin' or check_name == 2:
        BotHelper.role = 'admin'
        item1 = types.KeyboardButton('Создать голосование')
        item2 = types.KeyboardButton('Управлять голосованиями')
        item0 = types.KeyboardButton('Сменить аккаунт')
        mark.add(item1)
        mark.add(item2)
        mark.add(item0)
        if check_name == 2:
            bot.send_message(message.chat.id, 'Отлично, тебе доступна админ панель.\n'
                                              'Чтобы управлять опросами используй кнопки ниже.\n'
                                              'В случае ошибки пиши или для того чтобы вернуться'
                                              ' жми кнопку ниже \'Назад\'', reply_markup=mark)
        else:
            bot.send_message(message.chat.id, 'Чтобы управлять опросами используй кнопки ниже', reply_markup=mark)
        bot.register_next_step_handler(message, poll_first)
    elif flag == 0 and BotHelper.role == 'student' or check_name == 1:
        BotHelper.role = 'student'
        item0 = types.KeyboardButton('Сменить аккаунт')
        mark.add(item0)
        bot.send_message(message.chat.id, 'Вот список доступных голосований.\n'
                                          'В случае ошибки пиши или для того чтобы вернуться'
                                          ' жми кнопку ниже \'Назад\'', reply_markup=mark)
        answer_show(message)
    else:
        start(message)


@bot.message_handler(commands=["poll"])
def poll_first(message):
    if message.text == 'Сменить аккаунт':
        start(message)
        BotHelper.nick = ''
        return
    if message.text == 'Создать голосование':
        item1 = types.KeyboardButton('Анонимный')
        item2 = types.KeyboardButton('Публичный')
        mark = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        mark.add(item1)
        mark.add(item2)
        bot.send_message(message.chat.id, 'Для начала выбери тип голосования', reply_markup=mark)
        bot.register_next_step_handler(message, poll_types)
    elif message.text == 'Управлять голосованиями':
        answer_show(message)


def poll_types(message):
    if message.text == 'Анонимный':
        BotHelper.x = 0
    elif message.text == 'Публичный':
        BotHelper.x = 1
    else:
        bot.send_message(message.chat.id, 'Неизвестный тип')
        autorize(message, 0)
        return
    item1 = types.KeyboardButton('Один голос')
    item2 = types.KeyboardButton('Несколько вариантов ответов')
    item3 = types.KeyboardButton('Свой вариант')
    mark = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    mark.add(item1)
    mark.add(item2)
    mark.add(item3)
    bot.send_message(message.chat.id, 'Теперь выбери вид голосования', reply_markup=mark)
    bot.register_next_step_handler(message, poll_question)


def poll_question(message):
    if message.text == 'Один голос':
        BotHelper.y = 0
    elif message.text == 'Несколько вариантов ответов':
        BotHelper.y = 1
    elif message.text == 'Свой вариант':
        BotHelper.y = 2
    else:
        bot.send_message(message.chat.id, 'Неизвестный вид')
        autorize(message, 0)
        return
    bot.send_message(message.chat.id, 'Сейчас напиши вопрос голосования')
    bot.register_next_step_handler(message, first_answer)


def first_answer(message):
    tex = message.text
    if message.photo is not None:
        tex = str(message.photo[-1].file_id) + ' ' + str(message.caption)
    create_question = """INSERT INTO questions (question_list, type_question, type_answers) 
                         VALUES ("%s", "%d", "%d") """ % (tex, BotHelper.x, BotHelper.y)
    dal.execute_query(dal.connection, create_question)
    select_question_id = """SELECT count(id) FROM questions"""
    BotHelper.question_id = dal.execute_read_query(dal.connection, select_question_id)[0][0]
    bot.send_message(message.chat.id, 'Теперь напиши первый ответ')
    bot.register_next_step_handler(message, poll_answers)


def valid_name(message):
    flag_return = dal.validation(message.text)
    if flag_return == 0:
        bot.send_message(message.chat.id, 'Пользователь отсутствует в системе, прочь')
    if flag_return == 1 or flag_return == 2:
        select_users2 = f"""SELECT username, roles FROM users WHERE login = "%s" """ % message.text
        bot.send_message(message.chat.id,
                         'Привет,  %s' % dal.execute_read_query(dal.connection, select_users2)[0][0])
    return flag_return


def answer_show(message):
    BotHelper.question_step = 'showPoll'
    select_users = "SELECT id, question_list from questions"
    users = dal.execute_read_query(dal.connection, select_users)
    mark = types.InlineKeyboardMarkup()
    for user in users:
        stroka = str(user[0]) + '. ' + user[1]
        us = str(user[1]).split(' ')
        if is_base64(us[0]) and len(str(us[0])) > 60:
            item = types.InlineKeyboardButton(str(user[0]) + '. Вопрос с фото', callback_data=str(user[0]))
        else:
            item = types.InlineKeyboardButton(stroka, callback_data=str(user[0]))
        mark.add(item)
    bot.send_message(message.chat.id, 'Список доступных голосований:', reply_markup=mark)
    mark2 = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    item2 = types.KeyboardButton('Назад')
    mark2.add(item2)
    if BotHelper.role == 'student':
        item3 = types.KeyboardButton('Сменить аккаунт')
        mark2.add(item3)
    bot.send_message(message.chat.id, 'Чтобы вернуться назад нажми кнопку ниже', reply_markup=mark2)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    select_users = "SELECT id, question_list from questions"
    users = dal.execute_read_query(dal.connection, select_users)
    for user in users:
        if call.data == str(user[0]):
            BotHelper.question_step = 'showPoll'
            BotHelper.question_number = user[0]
            break
    if BotHelper.question_step == 'showPoll':
        poll_creation(call.message, user[1])
    else:
        x = str(call.data).split(' ')
        for usr in users:
            if x[0] == str(usr[0]):
                BotHelper.question_number = usr[0]
        if x[2] == 'RTYUIO':
            bot.send_message(call.message.chat.id, 'Напиши свой вариант ответа')
            bot.register_next_step_handler(call.message, answer_base, call.data)
        else:
            answer_base(call.message, call.data)


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


def answer_base(m, question):
    x = str(question).split(' ')
    if x[2] == 'RTYUIO':
        x[2] = str(m.text)
    select_answers = """SELECT answer_id, answer, login_user, question_id from answers 
                        WHERE login_user = "%s" AND question_id = "%d" """\
                     % (BotHelper.nick, BotHelper.question_number)
    ans = dal.execute_read_query(dal.connection, select_answers)
    select_type = """SELECT type_answers from questions
                     WHERE id = "%d" """ % BotHelper.question_number
    type_ans = dal.execute_read_query(dal.connection, select_type)
    for anss in ans:
        if type_ans[0][0] == 0 and anss[2] == BotHelper.nick and anss[3] == BotHelper.question_number:
            bot.send_message(m.chat.id, 'Ты уже голосовал, в этом опросе можно участвовать только один раз!')
            poll_result(m)
            return
        if int(anss[0]) == int(x[1]):
            bot.send_message(m.chat.id, 'Ты уже голосовал за этот вариант, но ты можешь выбрать и другие')
            poll_result(m)
            return
    create_answers = """
    INSERT INTO
        answers (answer, question_id, login_user, answer_id)
    VALUES
        ("%s", "%d", "%s", "%d") 
    """ % (x[2], BotHelper.question_number, BotHelper.nick, int(x[1]))
    dal.execute_query(dal.connection, create_answers)
    poll_result(m)


def poll_creation(message, question):
    BotHelper.question_step = 'Poll'
    select_question_id = """SELECT id, answer FROM answer_list WHERE question_id = "%d" """ % BotHelper.question_number
    users = dal.execute_read_query(dal.connection, select_question_id)
    mark = types.InlineKeyboardMarkup()
    for user in users:
        if user[1] == 'Свой вариант':
            tex = 'RTYUIO'
            tex = str(tex).split(' ')
        else:
            tex = str(user[1]).split(' ')
        item = types.InlineKeyboardButton(str(user[1]),
                                          callback_data=str(BotHelper.question_number) + ' '
                                                                                       + str(user[0]) + ' ' + tex[0])
        mark.add(item)
    if is_base64(str(question).split(' ')[0]) and len(str(question).split(' ')[0]) > 60:
        bot.send_photo(message.chat.id, str(question).split(' ')[0], caption=get_caption(str(question).split(' ')),
                       reply_markup=mark)
    else:
        bot.send_message(message.chat.id, question, reply_markup=mark)


def get_caption(beat_caption):
    return_string = ''
    for i in range(1, len(beat_caption)):
        return_string += beat_caption[i] + ' '
    return return_string


def poll_result(message):
    select_name_question = """SELECT question_list, type_question 
                              FROM questions WHERE  id = "%d" """ % BotHelper.question_number
    name_question = dal.execute_read_query(dal.connection, select_name_question)

    select_all_answers = """SELECT id, answer FROM answer_list WHERE question_id = "%d" """ % BotHelper.question_number
    all_answers = dal.execute_read_query(dal.connection, select_all_answers)

    count_answers = """SELECT count (answer) FROM answer_list WHERE question_id = "%d" """ % BotHelper.question_number
    count_answ = dal.execute_read_query(dal.connection, count_answers)

    select_answers = """SELECT count(login_user) FROM answers WHERE question_id = "%d" """ % BotHelper.question_number
    count = dal.execute_read_query(dal.connection, select_answers)

    if is_base64(str(name_question[0][0]).split(' ')[0]) and len(str(name_question[0][0]).split(' ')[0]) > 60:
        stat = str('Вопрос с фото')
    else:
        stat = str(name_question[0][0])
    stat += ' - Публичный опрос' + '\n\n' if name_question[0][1] == 1 else ' - Анонимный опрос' + '\n\n'
    pr = ['⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪',
          '🔴⚪⚪⚪⚪⚪⚪⚪⚪⚪',  # 1-10
          '🔴🔴⚪⚪⚪⚪⚪⚪⚪⚪',  # 11-20
          '🔴🔴🔴⚪⚪⚪⚪⚪⚪⚪',  # 21-30
          '🔴🔴🔴🔴⚪⚪⚪⚪⚪⚪',  # 31-40
          '🔴🔴🔴🔴🔴⚪⚪⚪⚪⚪',  # 41-50
          '🟢🟢🟢🟢🟢🟢⚪⚪⚪⚪',  # 51-60
          '🟢🟢🟢🟢🟢🟢🟢⚪⚪⚪',  # 61-70
          '🟢🟢🟢🟢🟢🟢🟢🟢⚪⚪',  # 71-80
          '🟢🟢🟢🟢🟢🟢🟢🟢🟢⚪',  # 81-90
          '🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢'   # 91-100
          ]
    n = 1
    for i in range(0, count_answ[0][0], 1):
        count_users_for_answer = """
        SELECT 
        count(login_user)
        FROM 
        answers 
        WHERE 
        question_id = "%s" and answer_id = "%s" """ \
                                 % (BotHelper.question_number, all_answers[i][0])
        answers = dal.execute_read_query(dal.connection, count_users_for_answer)

        list_users_for_answer = """
                SELECT 
                login_user,
                answer
                FROM 
                answers 
                WHERE 
                question_id = "%s" and answer_id = "%s" """ \
                                 % (BotHelper.question_number, all_answers[i][0])
        list_users = dal.execute_read_query(dal.connection, list_users_for_answer)
        names = "✋\n"
        choice = False
        for k in range(0, answers[0][0], 1):
            if name_question[0][1] == 1:
                names += list_users[k][0]
                if all_answers[i][1] == 'Свой вариант':
                    names += ' - ' + list_users[k][1]
                if k < answers[0][0]-1:
                    names += ", "
                    if all_answers[i][1] == 'Свой вариант':
                        names += '\n'
            else:
                if all_answers[i][1] == 'Свой вариант':
                    choice = True
                    names += list_users[k][1]
                if k < answers[0][0]-1:
                    names += ", "
                    if all_answers[i][1] == 'Свой вариант':
                        names += '\n'

        stat += '' + str(n) + ".  " + all_answers[i][1] + "   -   " + str(answers[0][0]) + "\n"
        if round(answers[0][0] / count[0][0] * 100) == 0:
            stat += '     ' + pr[0]
        for j in range(0, 100, 10):
            if j < round(answers[0][0] / count[0][0] * 100) <= j + 10:
                stat += '     ' + pr[(j+10)//10]
        stat += '' + "     -   " + str(round(answers[0][0] / count[0][0] * 100)) + "%\n"
        if name_question[0][1] == 1 or choice:
            stat += names  #
        stat += '' + '\n\n'
        n += 1
    stat += '' + "Всего проголосовало: " + str(count[0][0])
    bot.send_message(message.chat.id, '<b>'+stat+'</b>', parse_mode="html")


bot.polling(none_stop=True, interval=0)
