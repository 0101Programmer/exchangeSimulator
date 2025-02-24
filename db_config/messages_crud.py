import random
from datetime import datetime

import psycopg2.extras

from db_config.db_connection import get_connection


def create_message(msg_field, msg_type, msg_comment, msg_name):
    with get_connection() as conn:
        with conn.cursor() as curs:

            curs.execute('''
                INSERT INTO messages (message_field, message_type, message_comment, message_name) 
                VALUES (%s, %s, %s, %s)
            ''', (msg_field, msg_type, msg_comment, msg_name))
            conn.commit()

def get_all_messages():
    with get_connection() as conn:
        # запрос всех записей с авто-конвертацией в словарь
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as curs:
            curs.execute('SELECT * FROM messages')
            messages = curs.fetchall()
            return messages

def get_message_by_id(message_id):
    with get_connection() as conn:
        # запрос записи по id
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as curs:
            curs.execute('SELECT * FROM messages WHERE id=%s', (message_id, ))
            message = curs.fetchone()
            return message


def delete_all_messages():
    with get_connection() as conn:
        with conn.cursor() as curs:
            curs.execute('TRUNCATE TABLE messages RESTART IDENTITY')
    return {"message": "success"}

if __name__ == '__main__':
    print(get_all_messages())