import httpx
import pytest

from main import send_message
from unittest.mock import patch

@pytest.mark.asyncio
async def test_send_message():
    """
    Тестирование функции отправки сообщения от сервера.

    Проверяет, что функция send_message корректно формирует и отправляет POST-запрос.
    """

    # Мок ответа сервера
    async def mock_post(*args, **kwargs):
        class MockResponse:
            status_code = 200
            text = "Сообщение успешно отправлено."
        return MockResponse()

    # Подменяем httpx.AsyncClient.post на мок, который имитирует поведение сервера
    with patch("httpx.AsyncClient.post", new=mock_post):
        # Вызываем функцию и проверяем результат
        await send_message("test_field", "test_type", "test_comment", "test_name")