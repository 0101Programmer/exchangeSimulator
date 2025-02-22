import json

from fastapi import WebSocket
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, WebSocketDisconnect, Request, Response, Body

from db_config.orders_crud import get_all_orders

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# HTML страница для тестирования WebSocket
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>WebSocket Test</title>
    </head>
    <body>
        <h1>WebSocket Test</h1>
        <input type="text" id="messageInput" placeholder="Введите сообщение">
        <button onclick="sendMessage()">Отправить</button>
        <ul id="messages"></ul>
        <script>
            const ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                const messages = document.getElementById('messages');
                const message = document.createElement('li');
                message.textContent = event.data;
                messages.appendChild(message);
            };
            function sendMessage() {
                const input = document.getElementById("messageInput");
                ws.send(input.value);
                input.value = '';
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("main_exchange_page.html",
                                      {"request": request, "header": "Симулятор биржи", "title": "Exchange Page",
                                       })

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Принимаем соединение
    try:
        while True:
            # Отправляем данные из get_all_orders() сразу при подключении
            orders = get_all_orders()
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
                for order in orders
            ]
            await websocket.send_text(json.dumps(orders_json))
            # Держим соединение открытым
            while True:
                await websocket.receive_text()
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)