import pytest
from fastapi.testclient import TestClient

from main import app


def test_receive_message():
    """
    Тестирование эндпоинта `/api/v1/receive_message/`.

    Проверяет обработку данных:
        - Отправка валидного POST-запроса с правильными полями.
        - Проверка, что сервер возвращает статус-код 200 и JSON `{ "status": "success" }`.
    """

    client = TestClient(app)

    # Отправляем POST-запрос
    response = client.post(
        "/api/v1/receive_message/",
        json={
            "msg_field": "test_field",
            "msg_type": "test_type",
            "msg_comment": "test_comment",
            "msg_name": "test_name"
        }
    )

    # Проверяем ответ
    assert response.status_code == 200
    assert response.json() == {"status": "success"}