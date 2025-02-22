import ast

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Response, Body
from fastapi.responses import JSONResponse

from typing import List
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from db_config.orders_crud import get_all_orders, get_order_by_id, get_order_by_side_and_instrument

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Список подключенных клиентов
connected_clients = []


# WebSocket для веб-интерфейса биржи
@app.websocket("/ws/{phone_number}")
async def websocket_endpoint(websocket: WebSocket, phone_number: int):
    await websocket.accept()
    print(phone_number)
    await websocket.send_text("test")

    '''
    # Добавляем клиента в список подключенных
    connected_clients.append({"websocket": websocket, "phone_number": phone_number})
    # Приветственное сообщение для нового клиента
    welcome_message = f"Привет, пользователь с номером телефона {phone_number}! Добро пожаловать в exchangeSimulator!"
    await websocket.send_text(welcome_message)

    # Отправляем сообщения из очереди (если они есть)
    for message in order_queue:
        await websocket.send_text(message)

    try:
        while True:
            data = await websocket.receive_text()
            message = f"{phone_number}: {data}"
            # Добавляем сообщение в очередь
            order_queue.append(message)
            # Отправляем сообщение всем подключенным клиентам
            for client in connected_clients:
                await client["websocket"].send_text(message)
    except WebSocketDisconnect:
        # Удаляем клиента из списка при отключении
        connected_clients.remove({"websocket": websocket, "phone_number": phone_number})
        '''



# Веб-страница для входа по номеру телефона
@app.get("/", response_class=HTMLResponse)
async def exchange_interface(request: Request):
    orders = get_all_orders()
    return templates.TemplateResponse("exchange_page.html",
                                      {"request": request, "header": "Симулятор биржи", "title": "Exchange Page",
                                       "orders": orders})

@app.post("/receive_data")
async def receive_data(request: Request):
    data = await request.json()
    order_id = get_order_by_id(data["order_id"])
    order_amount = float(data["order_amount"]) if data["order_amount"] != '' else 1

    buy_side = get_order_by_side_and_instrument("Buy", order_id["instrument"]) if (
        get_order_by_side_and_instrument("Buy", order_id["instrument"])) else None
    sell_side = get_order_by_side_and_instrument("Sell", order_id["instrument"]) if (
        get_order_by_side_and_instrument("Sell", order_id["instrument"])) else None

    return JSONResponse(content={"buy_side_price": round(buy_side["price"] * order_amount, 5),
                                 "sell_side_price": round(sell_side["price"] * order_amount, 5), })
