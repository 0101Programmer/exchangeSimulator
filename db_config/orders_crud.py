import random
from datetime import datetime

from db_config.db_connection import get_connection

status_list = ["Active", "Filled", "Rejected", "Cancelled"]
side_list = ["Buy", "Sell"]
amount_list = [10_000.00, 20_000.00, 30_000.00, 50_000.00, 60_000.00, 70_000.00, 100_000.00,
               350_000.00, 500_000.00]
instrument_list = ["CNH/RUB", "EUR/RUB", "EUR/USD", "USD/RUB", "TRY/RUB", "BYN/RUB"]

def create_order():
    # Вычисляем значения в Python
    creation_time = datetime.now()
    change_time = datetime.now()
    status = random.choice(status_list)
    side = random.choice(side_list)
    price = random.uniform(3, 65)
    amount = random.choice(amount_list)
    instrument = random.choice(instrument_list)

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
        with conn.cursor() as curs:
            curs.execute('SELECT * FROM orders')
            orders = curs.fetchall()
            return orders


if __name__ == '__main__':
    # создать 10 заявок на бирже
    # for i in range(10):
    #     create_order()

    # получить все заявки из таблицы
    print(get_all_orders())