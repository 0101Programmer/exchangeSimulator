import random
from datetime import datetime

import psycopg2.extras

from db_config.db_connection import get_connection

status_list = ["Active", "Filled", "Rejected", "Cancelled"]
side_list = ["Buy", "Sell"]
amount_list = [10_000.00, 20_000.00, 30_000.00, 50_000.00, 60_000.00, 70_000.00, 100_000.00,
               350_000.00, 500_000.00]
instrument_list = ["CNH/RUB", "EUR/RUB", "EUR/USD", "USD/RUB", "TRY/RUB", "BYN/RUB"]

def create_order(side_idx, instrument_idx):
    # Вычисляем значения в Python
    creation_time = datetime.now()
    change_time = datetime.now()
    status = random.choice(status_list)
    side = side_list[side_idx]
    price = random.uniform(3, 65)
    amount = random.choice(amount_list)
    instrument = instrument_list[instrument_idx]

    # SQL-запрос с параметрами
    query = '''
        INSERT INTO orders (creation_time, change_time, status, side, price, amount, instrument) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        '''
    with get_connection() as conn:
        with conn.cursor() as curs:

            # Передаем параметры в запрос
            curs.execute(query, (creation_time, change_time, status, side, price, amount, instrument))
            conn.commit()

def get_all_orders():
    with get_connection() as conn:
        # запрос всех записей с авто-конвертацией в словарь
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as curs:
            curs.execute('SELECT * FROM orders')
            orders = curs.fetchall()
            return orders

def get_order_by_id(order_id):
    with get_connection() as conn:
        # запрос записи по id
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as curs:
            curs.execute('SELECT * FROM orders WHERE id=%s', (order_id, ))
            order = curs.fetchone()
            return order

def get_order_by_side_and_instrument(order_side, order_instrument):
    with get_connection() as conn:
        # запрос записи по side и instrument
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as curs:
            curs.execute('SELECT * FROM orders WHERE side=%s AND instrument=%s', (order_side, order_instrument, ))
            order = curs.fetchone()
            return order

def update_all_orders():
    with get_connection() as conn:
        with conn.cursor() as curs:
            curs.execute('TRUNCATE TABLE orders RESTART IDENTITY')
    for i, instrument in enumerate(instrument_list):
        create_order(0, i)
        create_order(1, i)
    return get_all_orders()


def delete_all_orders():
    with get_connection() as conn:
        with conn.cursor() as curs:
            curs.execute('TRUNCATE TABLE orders RESTART IDENTITY')
    return {"message": "success"}


if __name__ == '__main__':
    # создание заявок в таблице

    # for i, instrument in enumerate(instrument_list):
    #     create_order(0, i)
    #     create_order(1, i)

    # получить все заявки из таблицы
    print(get_all_orders())

    # обновить все заявки из таблицы
    print(update_all_orders())

    # удалить все заявки из таблицы

    # delete_all_orders()
