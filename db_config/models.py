from pydantic import BaseModel

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
        curs.execute('''CREATE TABLE IF NOT EXISTS messages
                (ID serial PRIMARY KEY NOT NULL,
                MESSAGE_FIELD TEXT NOT NULL,\
                MESSAGE_TYPE TEXT NOT NULL,
                MESSAGE_COMMENT TEXT NOT NULL,
                MESSAGE_NAME TEXT NOT NULL);''')
        conn.commit()


# Модель для сообщений от сервера
class Message(BaseModel):
    msg_field: str
    msg_type: str
    msg_comment: str
    msg_name: str