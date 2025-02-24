import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import random
from db_config.orders_crud import create_order, status_list, side_list, amount_list, instrument_list

class TestCreateOrder(unittest.TestCase):

    @patch('db_config.orders_crud.get_connection')
    def test_create_order(self, mock_get_connection):
        # Мокируем соединение с базой данных и курсор
        mock_conn = MagicMock()
        mock_curs = MagicMock()

        # Настраиваем мок для get_connection
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_curs

        # Вызываем функцию
        create_order(0, 1)

        # Проверяем, что execute был вызван
        mock_curs.execute.assert_called_once()

        # Проверяем, что commit был вызван
        mock_conn.commit.assert_called_once()

if __name__ == '__main__':
    unittest.main()