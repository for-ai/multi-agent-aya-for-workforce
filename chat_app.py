from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from typing import List, Dict

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_modes: Dict[int, str] = {}

    async def connect(self, websocket: WebSocket, language: str):
        self.active_connections.append(websocket)
        self.connection_modes[id(websocket)] = language

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        del self.connection_modes[id(websocket)]

    async def broadcast(self, message: str, language: str):
        for connection in self.active_connections:
            if self.connection_modes[id(connection)] == language:
                await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    language = await websocket.receive_text()
    if language not in {"English", "French", "Spanish"}:
        await websocket.close()
        return

    await manager.connect(websocket, language)

    try:
        while True:
            data = await websocket.receive_text()
            print(data)
            await manager.broadcast(f"{data}", language)
    except Exception as e:
        print(f"Exception: {e}")
        manager.disconnect(websocket)

# Serve static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")
