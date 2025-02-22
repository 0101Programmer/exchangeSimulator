import ast
import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Response, Body
from fastapi.responses import JSONResponse

from typing import List
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from db_config.orders_crud import get_all_orders, get_order_by_id, get_order_by_side_and_instrument, update_all_orders

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

orders = get_all_orders()

# Список подключенных клиентов
connected_clients = []


# WebSocket для веб-интерфейса биржи
@app.websocket("/ws/{phone_number}")
async def websocket_endpoint(websocket: WebSocket, phone_number: int):
    await websocket.accept()
    print(f"Client connected: {phone_number}")

    try:
        while True:
            # Отправляем данные клиенту каждые 10 секунд
            await asyncio.sleep(0)  # Интервал обновления
            data = {"message": "Updated data", "phone_number": phone_number}
            await websocket.send_json(data)  # Отправляем JSON-данные
    except WebSocketDisconnect:
        print(f"Client disconnected: {phone_number}")


# Веб-страница для входа по номеру телефона
@app.get("/", response_class=HTMLResponse)
async def exchange_interface(request: Request):
    global orders
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



