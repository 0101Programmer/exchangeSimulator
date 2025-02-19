from db_config.db_connection import get_connection

with get_connection() as conn:
    with conn.cursor() as curs:
        curs.execute('''CREATE TABLE IF NOT EXISTS orders
        (ID serial PRIMARY KEY NOT NULL,
        CREATION_TIME TIMESTAMP NOT NULL,\
        CHANGE_TIME TIMESTAMP NOT NULL,
        STATUS TEXT NOT NULL,
        SIDE TEXT NOT NULL,
        PRICE real NOT NULL,
        AMOUNT real NOT NULL,
        INSTRUMENT TEXT NOT NULL);''')
        conn.commit()