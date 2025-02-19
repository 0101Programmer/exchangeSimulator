from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Response
from typing import List
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")

