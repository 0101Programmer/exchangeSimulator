import asyncio
import json
from contextlib import asynccontextmanager

from fastapi import WebSocket
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, WebSocketDisconnect, Request, Response, Body

from db_config.orders_crud import get_all_orders, update_all_orders

# Глобальная переменная для хранения и периодического обновления табличных данных
global_orders = []

# подключённые клиенты
active_connections = []



# Функция для периодического обновления данных в таблице заявок
async def periodic_update():
    global global_orders
    while True:
        # Обновляем данные с помощью update_all_orders()
        global_orders = update_all_orders()

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

        # Ждем 45 секунд перед следующей отправкой
        await asyncio.sleep(45)


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
        print(f"Ошибка: {e}")
    finally:
        active_connections.remove(websocket)
        await websocket.close()


# Запуск сервера
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)