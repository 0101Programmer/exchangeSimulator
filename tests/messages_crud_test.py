import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock

from db_config.messages_crud import create_message


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


if __name__ == '__main__':
    unittest.main()