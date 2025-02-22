from fastapi import WebSocket
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, WebSocketDisconnect, Request, Response, Body

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
            # Получаем сообщение от клиента
            data = await websocket.receive_text()
            # Отправляем обратно полученное сообщение с добавлением текста
            await websocket.send_text(f"Сообщение от сервера: {data}")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        await websocket.close()  # Закрываем соединение при выходе

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)