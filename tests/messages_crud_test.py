import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock

from db_config.messages_crud import create_message, get_all_messages, get_message_by_id, delete_all_messages


class TestMessagesCRUD(unittest.TestCase):

    @patch('db_config.messages_crud.get_connection')
    def test_create_message(self, mock_get_connection):
        """
        Тестирование функции create_message.
        Проверяет, что функция корректно выполняет SQL-запрос и сохраняет запись в БД.
        """
        # Мокируем соединение с базой данных и курсор
        mock_conn = MagicMock()
        mock_curs = MagicMock()

        # Настраиваем мок для get_connection
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_curs

        create_message("d860ff6c-96bc-47e2-9c01-84b2e0d3656a", "string", "Идентификатор успешной подписки", "SuccessInfo")

        # Проверяем, что execute был вызван
        mock_curs.execute.assert_called_once()

        # Проверяем, что commit был вызван
        mock_conn.commit.assert_called_once()

        # Проверяем параметры execute
        args, kwargs = mock_curs.execute.call_args
        query, params = args

        # Проверяем SQL-запрос
        self.assertIn("INSERT INTO messages", query)

        # Проверяем параметры
        msg_field, msg_type, msg_comment, msg_name = params

        # Проверяем типы параметров
        self.assertIsInstance(msg_field, str)
        self.assertIsInstance(msg_type, str)
        self.assertIsInstance(msg_comment, str)
        self.assertIsInstance(msg_name, str)

        # Проверяем значения параметров
        self.assertEqual(msg_field, "d860ff6c-96bc-47e2-9c01-84b2e0d3656a")
        self.assertEqual(msg_type, "string")
        self.assertEqual(msg_comment, "Идентификатор успешной подписки")
        self.assertEqual(msg_name, "SuccessInfo")

        self.assertEqual(len(params), 4)  # Ожидаем 4 параметра

    @patch('db_config.messages_crud.get_connection')
    def test_get_all_messages(self, mock_get_connection):
        """
        Тестирование функции get_all_messages.
        Проверяет, что функция корректно выполняет SQL-запрос и возвращает ожидаемые данные.
        """
        # Мокируем соединение с базой данных и курсор
        mock_conn = MagicMock()
        mock_curs = MagicMock()

        # Настраиваем мок для get_connection
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_curs

        # Моковые данные для имитации ответа базы данных
        mock_data = [
            {'id': 1,
             'message_field': 'success',
             'message_type': 'string',
             'message_comment': 'Изменение котировок',
             'message_name': 'MarketDataUpdate'},

            {'id': 2,
             'message_field': '1',
             'message_type': 'integer',
             'message_comment': 'Идентификатор инструмента, на котировки которого запрошена подписка',
             'message_name': 'SubscribeMarketData'}
        ]
        # Настройка мока для curs.fetchall()
        mock_curs.fetchall.return_value = mock_data

        # Вызываем тестируемую функцию
        result = get_all_messages()

        # Проверяем, что execute был вызван с правильным запросом
        mock_curs.execute.assert_called_once_with('SELECT * FROM messages')

        # Проверяем, что функция вернула правильные данные
        assert result == mock_data, f"Ожидалось {mock_data}, получено {result}"

    @patch('db_config.messages_crud.get_connection')
    def test_get_message_by_id(self, mock_get_connection):
        """
        Тестирование функции get_message_by_id для запроса сообщения по message_id.
        """
        # Создаем мок для соединения
        mock_conn = MagicMock()
        mock_curs = MagicMock()

        # Настройка мока для get_connection
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_curs

        # Моковые данные для имитации ответа базы данных
        mock_data = {'id': 1,
                     'message_field': 'success',
                     'message_type': 'string',
                     'message_comment': 'Изменение котировок',
                     'message_name': 'MarketDataUpdate'}

        # Настройка мока для curs.fetchone(), чтобы он возвращал тестовые данные
        mock_curs.fetchone.return_value = mock_data

        # Вызываем тестируемую функцию
        result = get_message_by_id(1)

        # Проверяем, что execute был вызван с правильным запросом и параметрами
        mock_curs.execute.assert_called_once_with('SELECT * FROM messages WHERE id=%s', (1,))

        # Проверяем, что функция вернула правильные данные
        assert result == mock_data, f"Ожидалось {mock_data}, получено {result}"

    @patch('db_config.messages_crud.get_connection')
    def test_delete_all_messages(self, mock_get_connection):
        """
        Тестирование функции delete_all_messages для удаления всех записей из БД.
        Проверяет, что функция выполняет TRUNCATE и возвращает правильный ответ.
        """
        # Создаем мок для соединения
        mock_conn = MagicMock()
        mock_curs = MagicMock()

        # Настройка мока для get_connection
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_curs

        # Вызываем тестируемую функцию
        result = delete_all_messages()

        # Проверяем, что execute был вызван с правильным запросом
        mock_curs.execute.assert_called_once_with('TRUNCATE TABLE messages RESTART IDENTITY')

        # Проверяем, что функция вернула правильный ответ
        assert result == {"message": "success"}, f"Ожидалось {{'message': 'success'}}, получено {result}"


if __name__ == '__main__':
    unittest.main()