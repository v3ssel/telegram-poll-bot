import sqlite3
import time
from sqlite3 import Error
from datetime import datetime

def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path, check_same_thread=False)
        print("Connection to SQLite DB successful", datetime.fromtimestamp(time.time()))
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully", datetime.fromtimestamp(time.time()))
    except Error as e:
        print(f"The error '{e}' occurred")


def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred", datetime.fromtimestamp(time.time()))


def validation(message_text: object) -> object:
    flag_return = 0  # пользователь не найден
    select_users = "SELECT login, roles from users"
    users = execute_read_query(connection, select_users)
    err_code = 0
    for user in users:
        if user[0] == message_text:
            flag_return = 1  # найден обычный пользователь
            if user[1] == 'admin':
                flag_return = 2  # найден админ
    return flag_return


connection = create_connection("dataBase")  # установили связь с БД

create_users_table = """
CREATE TABLE IF NOT EXISTS users (
id INTEGER PRIMARY KEY AUTOINCREMENT,
login TEXT NOT NULL,
roles TEXT NOT NULL,
campus TEXT NOT NULL,
username TEXT NOT NULL
);
"""

create_users = """
INSERT INTO
    users (login, roles, campus, username)
VALUES
    ('stironni', 'student', 'Kzn', 'Илья'),
    ('michaelc', 'student', 'Kzn', 'Илья'),
    ('stephanr', 'admin', 'Kzn', 'Андрей'),
    ('valkyrie', 'admin', 'Kzn', 'Андрей'),
    ('snappmas', 'student', 'Kzn', 'Дима'),
    ('studebaa', 'student', 'Kzn', 'Дима'),
    ('stevenso', 'admin', 'Kzn', 'Данила'),
    ('hasturka', 'admin', 'Kzn', 'Данила'),
    ('jenellep', 'student', 'Kzn', 'Сергей'),
    ('mocharar', 'student', 'Kzn', 'Сергей');
"""
# создаем и заполняем таблицу users

create_questions_table = """
CREATE TABLE IF NOT EXISTS questions (
id INTEGER PRIMARY KEY AUTOINCREMENT,
question_list TEXT NOT NULL,
type_question NUMBER(1),
type_answers INTEGER
);
"""
# создаем таблицу questions

create_answer_list_table = """
CREATE TABLE IF NOT EXISTS answer_list (
id INTEGER PRIMARY KEY AUTOINCREMENT,
answer TEXT NOT NULL,
question_id INTEGER,
FOREIGN KEY (question_id) REFERENCES questions (id)
);
"""
# создаем таблицу answer_list

create_answers_table = """
CREATE TABLE IF NOT EXISTS answers (
id INTEGER PRIMARY KEY AUTOINCREMENT,
answer TEXT NOT NULL,
question_id INTEGER ,
login_user TEXT NOT NULL,
answer_id INTEGER NOT NULL,
FOREIGN KEY (question_id) REFERENCES questions (id),
FOREIGN KEY (login_user) REFERENCES users (login)
);
"""
# создаем таблицу answers
# execute_query(connection, create_users_table)
# execute_query(connection, create_users)
# execute_query(connection, create_questions_table)
# execute_query(connection, create_answer_list_table)
# execute_query(connection, create_answers_table)


select_users = "SELECT * from questions"
users = execute_read_query(connection, select_users)
for user in users:
    print(user)

print('')

select_users = "SELECT * from answer_list"
users = execute_read_query(connection, select_users)
for user in users:
    print(user)

print('')

select_users = "SELECT * from answers"
users = execute_read_query(connection, select_users)
for user in users:
    print(user)
