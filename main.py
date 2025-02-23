import asyncio
import json
from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI, Request
from fastapi import WebSocket, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from db_config.messages_crud import create_message
from db_config.models import Message
from db_config.orders_crud import update_all_orders

# Глобальная переменная для хранения и периодического обновления табличных данных
global_orders = []

# Глобальная переменная для хранения времени периодического обновления табличных данных
refresh_sleep_time = 45

# подключённые клиенты
active_connections = []


async def send_message(msg_field, msg_type, msg_comment, msg_name):
    url = "http://127.0.0.1:8000/api/v1/receive_message/"
    data = {
        "msg_field": str(msg_field),
        "msg_type": str(msg_type),
        "msg_comment": str(msg_comment),
        "msg_name": str(msg_name)
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data, headers=headers, timeout=10)
            if response.status_code == 200:
                print("Сообщение успешно отправлено.")
            else:
                print(f"Ошибка при отправке сообщения: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Ошибка при отправке POST-запроса: {str(e)}")


# Функция для периодического обновления данных в таблице заявок
async def periodic_update():
    global global_orders
    while True:
        # Обновляем данные с помощью update_all_orders()
        global_orders = update_all_orders()
        # отправка сообщения MarketDataUpdate
        await send_message("success", "string", "Изменение котировок", "MarketDataUpdate")

        # Преобразуем datetime в ISO формат для JSON
        orders_json = [
            {
                "id": order["id"],
                "creation_time": order["creation_time"].isoformat(),
                "change_time": order["change_time"].isoformat(),
                "status": order["status"],
                "side": order["side"],
                "price": float(order["price"]),
                "amount": float(order["amount"]),
                "instrument": order["instrument"]
            }
            for order in global_orders
        ]

        # Отправляем обновленные данные всем подключенным клиентам
        for connection in active_connections:
            await connection.send_text(json.dumps(orders_json))

        # Ждем перед следующей отправкой
        await asyncio.sleep(refresh_sleep_time)


# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запускаем фоновую задачу при старте приложения
    task = asyncio.create_task(periodic_update())  # Создаем задачу
    yield  # Приложение работает
    # Останавливаем фоновую задачу при завершении приложения
    task.cancel()  # Отменяем задачу
    try:
        await task  # Ожидаем завершения задачи
    except asyncio.CancelledError:
        print("Фоновая задача остановлена")

app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("main_exchange_page.html",
                                      {"request": request, "header": "Симулятор биржи", "title": "Exchange Page",
                                       })

# WebSocket-эндпоинт
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Принимаем соединение
    active_connections.append(websocket)
    try:
        # Отправляем текущие данные при подключении
        orders_json = [
            {
                "id": order["id"],
                "creation_time": order["creation_time"].isoformat(),
                "change_time": order["change_time"].isoformat(),
                "status": order["status"],
                "side": order["side"],
                "price": float(order["price"]),
                "amount": float(order["amount"]),
                "instrument": order["instrument"]
            }
            for order in global_orders
        ]
        await websocket.send_text(json.dumps(orders_json))

        # Держим соединение открытым
        while True:
            await websocket.receive_text()  # Ожидаем сообщения от клиента
    except Exception as e:
        await send_message("error", "string", f"Ошибка: {e}", "ErrorInfo")
        print(f"Ошибка: {e}")
    finally:
        active_connections.remove(websocket)
        await websocket.close()



# API эндпоинт для приема сообщений от сервера и сохранения их в БД
@app.post("/api/v1/receive_message/")
async def receive_message(message: Message):
    try:
        create_message(message.msg_field, message.msg_type, message.msg_comment, message.msg_name)
        return {"status": "success"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при сохранении сообщения: {str(e)}")


# Запуск сервера
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)