import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock

from db_config.orders_crud import create_order, status_list, amount_list, get_all_orders, get_order_by_id, \
    get_order_by_side_and_instrument, update_all_orders, instrument_list, delete_all_orders


class TestOrdersCRUD(unittest.TestCase):

    @patch('db_config.orders_crud.get_connection') # Мокируем get_connection в orders_crud
    def test_create_order(self, mock_get_connection):
        """
        Тестирование функции create_order.
        Проверяет, что функция корректно выполняет SQL-запрос и сохраняет запись в БД.
        """
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

        # Проверяем параметры execute
        args, kwargs = mock_curs.execute.call_args
        query, params = args

        # Проверяем SQL-запрос
        self.assertIn("INSERT INTO orders", query)

        # Проверяем параметры
        creation_time, change_time, status, side, price, amount, instrument = params

        # Проверяем типы и значения параметров
        self.assertIsInstance(creation_time, datetime)
        self.assertIsInstance(change_time, datetime)
        self.assertIn(status, status_list)
        self.assertEqual(side, "Buy")
        self.assertGreaterEqual(price, 3)
        self.assertLessEqual(price, 65)
        self.assertIn(amount, amount_list)
        self.assertEqual(instrument, "EUR/RUB")

    @patch('db_config.orders_crud.get_connection')
    def test_get_all_orders(self, mock_get_connection):
        """
        Тестирование функции get_all_orders.
        Проверяет, что функция корректно выполняет SQL-запрос и возвращает ожидаемые данные.
        """
        # Создаем мок для соединения
        mock_conn = MagicMock()
        mock_curs = MagicMock()

        # Настройка мока для get_connection
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_curs

        # Моковые данные для имитации ответа базы данных
        mock_data = [
            {"id": 1,
             "creation_time": datetime.now(),
             "change_time": datetime.now(),
             "status": "Active",
             "side": "Buy",
             "price": 100.5,
             "amount": 50_000.0,
             "instrument": "EUR/RUB"},

            {"id": 2,
             "creation_time": datetime.now(),
             "change_time": datetime.now(),
             "status": "Filled",
             "side": "Sell",
             "price": 98.7,
             "amount": 30_000.0,
             "instrument": "USD/RUB"}
        ]
        # Настройка мока для curs.fetchall()
        mock_curs.fetchall.return_value = mock_data

        # Вызываем тестируемую функцию
        result = get_all_orders()

        # Проверяем, что execute был вызван с правильным запросом
        mock_curs.execute.assert_called_once_with('SELECT * FROM orders')

        # Проверяем, что функция вернула правильные данные
        assert result == mock_data, f"Ожидалось {mock_data}, получено {result}"

    @patch('db_config.orders_crud.get_connection')
    def test_get_order_by_id(self, mock_get_connection):
        """
        Тестирование функции get_order_by_id для существующего order_id.
        """
        # Создаем мок для соединения
        mock_conn = MagicMock()
        mock_curs = MagicMock()

        # Настройка мока для get_connection
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_curs

        # Моковые данные для имитации ответа базы данных
        mock_data = {
            "id": 1,
            "creation_time": datetime.now(),
            "change_time": datetime.now(),
            "status": "Active",
            "side": "Buy",
            "price": 100.5,
            "amount": 50_000.0,
            "instrument": "EUR/RUB"
        }

        # Настройка мока для curs.fetchone(), чтобы он возвращал тестовые данные
        mock_curs.fetchone.return_value = mock_data

        # Вызываем тестируемую функцию
        result = get_order_by_id(1)

        # Проверяем, что execute был вызван с правильным запросом и параметрами
        mock_curs.execute.assert_called_once_with('SELECT * FROM orders WHERE id=%s', (1,))

        # Проверяем, что функция вернула правильные данные
        assert result == mock_data, f"Ожидалось {mock_data}, получено {result}"

    @patch('db_config.orders_crud.get_connection')
    def test_get_order_by_side_and_instrument(self, mock_get_connection):
        """
        Тестирование функции get_order_by_side_and_instrument для нахождения записи в БД
        по параметру side и instrument.
        """
        # Создаем мок для соединения

        mock_conn = MagicMock()
        mock_curs = MagicMock()

        # Настройка мока для get_connection
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_curs

        # Моковые данные для имитации ответа базы данных
        mock_data = {
            "id": 1,
            "creation_time": datetime.now(),
            "change_time": datetime.now(),
            "status": "Active",
            "side": "Sell",
            "price": 100.5,
            "amount": 50_000.0,
            "instrument": "CNH/RUB"
        }
        # Настройка мока для curs.fetchone(), чтобы он возвращал тестовые данные
        mock_curs.fetchone.return_value = mock_data

        # Вызываем тестируемую функцию
        result = get_order_by_side_and_instrument("Sell", "CNH/RUB")

        # Проверяем, что execute был вызван с правильным запросом и параметрами
        mock_curs.execute.assert_called_once_with('SELECT * FROM orders WHERE side=%s AND instrument=%s',
                                                  ("Sell", "CNH/RUB"))

        # Проверяем, что функция вернула правильные данные
        assert result == mock_data, f"Ожидалось {mock_data}, получено {result}"

    @patch('db_config.orders_crud.get_connection')
    @patch('db_config.orders_crud.create_order')
    @patch('db_config.orders_crud.get_all_orders')
    def test_update_all_orders(self, mock_get_all_orders, mock_create_order, mock_get_connection):
        """
        Тестирование функции update_all_orders для полного обновления записей в БД.
        Проверяет, что функция правильно очищает таблицу и создает новые записи.
        """

        # Создаем мок для соединения
        mock_conn = MagicMock()
        mock_curs = MagicMock()

        # Настройка мока для get_connection
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_curs

        # Моковые данные для имитации ответа базы данных
        mock_data = [
            {"id": 1,
             "creation_time": datetime.now(),
             "change_time": datetime.now(),
             "status": "Active",
             "side": "Buy",
             "price": 100.5,
             "amount": 50_000.0,
             "instrument": "EUR/RUB"},

            {"id": 2,
             "creation_time": datetime.now(),
             "change_time": datetime.now(),
             "status": "Filled",
             "side": "Sell",
             "price": 98.7,
             "amount": 30_000.0,
             "instrument": "USD/RUB"}
        ]

        mock_get_all_orders.return_value = mock_data

        # Вызываем тестируемую функцию
        result = update_all_orders()

        # Проверяем, что TRUNCATE был выполнен
        mock_curs.execute.assert_called_once_with('TRUNCATE TABLE orders RESTART IDENTITY')

        # Проверяем, что create_order была вызвана для каждого инструмента и каждой стороны
        expected_calls = []
        # список ожидаемых вызовов в формате (side_idx, instrument_idx):
        for i in range(len(instrument_list)):
            expected_calls.append((0, i))  # side_idx=0 (Buy)
            expected_calls.append((1, i))  # side_idx=1 (Sell)
        # expected_calls = [(0, 0), (1, 0), (0, 1), (1, 1), ...]

        actual_calls = [args for args, _ in mock_create_order.call_args_list]
        # actual_calls = [(0, 0), (1, 0), (0, 1), ...]
        assert len(actual_calls) == len(
            expected_calls), f"Ожидалось {len(expected_calls)} вызовов create_order, получено {len(actual_calls)}"
        assert set(actual_calls) == set(expected_calls), f"Ожидались вызовы {expected_calls}, получены {actual_calls}"

        # Проверяем, что функция вернула правильные данные
        assert result == mock_data, f"Ожидалось {mock_data}, получено {result}"

    @patch('db_config.orders_crud.get_connection')
    def test_delete_all_orders(self, mock_get_connection):
        """
        Тестирование функции delete_all_orders для удаления всех записей из БД.
        Проверяет, что функция выполняет TRUNCATE и возвращает правильный ответ.
        """
        # Создаем мок для соединения
        mock_conn = MagicMock()
        mock_curs = MagicMock()

        # Настройка мока для get_connection
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_curs

        # Вызываем тестируемую функцию
        result = delete_all_orders()

        # Проверяем, что execute был вызван с правильным запросом
        mock_curs.execute.assert_called_once_with('TRUNCATE TABLE orders RESTART IDENTITY')

        # Проверяем, что функция вернула правильный ответ
        assert result == {"message": "success"}, f"Ожидалось {{'message': 'success'}}, получено {result}"





if __name__ == '__main__':
    unittest.main()