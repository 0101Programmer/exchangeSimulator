import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.mark.asyncio
async def test_websocket():
    """
    Тестирование функции обработки WebSocket-соединения.
    Проверяет, что сервер корректно устанавливает соединение и отправляет данные в правильном формате.

    Шаги теста:
    1. Установка соединения с WebSocket-эндпоинтом `/ws`.
    2. Получение данных от сервера.
    3. Проверка, что полученные данные являются списком.
    4. Если список не пустой, проверка каждого элемента:
       - Каждый элемент должен быть словарем.
       - Словари должны содержать ожидаемые поля: `id`, `creation_time`, `change_time`, `status`, `side`, `price`, `amount`, `instrument`.

    Ожидаемый результат:
    - Соединение успешно установлено.
    - Данные имеют правильный формат (список словарей).
    - Каждый словарь содержит все ожидаемые поля.
    """
    client = TestClient(app)

    # Устанавливаем WebSocket-соединение
    with client.websocket_connect("/ws") as websocket:
        # Получаем данные от сервера
        data = websocket.receive_json()

        # Проверяем, что данные — это список
        assert isinstance(data, list)

        if len(data) > 0:
            # Проверяем, что каждый элемент списка — это словарь
            assert all(isinstance(item, dict) for item in data)

            # Проверяем, что словари содержат ожидаемые поля
            expected_fields = {"id", "creation_time", "change_time", "status", "side", "price", "amount", "instrument"}
            assert all(set(item.keys()) == expected_fields for item in data)