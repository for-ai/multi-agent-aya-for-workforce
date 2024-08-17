from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from typing import List, Dict
import json
import os
import requests

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_modes: Dict[int, str] = {}
        self.user_feedback: Dict[str, List[Dict]] = {}

        self.language_to_team = {
            'English': 'TeamA',
            'Hindi': 'TeamB',
            'Spanish': 'TeamC',
            'Persian': 'TeamD'
        }

    async def connect(self, websocket: WebSocket, language: str):
        self.active_connections.append(websocket)
        self.connection_modes[id(websocket)] = language

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        del self.connection_modes[id(websocket)]

    async def broadcast(self, sender: str, translator_message: dict):
        for connection in self.active_connections:
            team_name = self.language_to_team.get(self.connection_modes[id(connection)])
            team_message = translator_message.get(team_name)
            await connection.send_text(json.dumps({"sender": sender, "message": team_message}))


    def add_feedback(self, sender: str, feedback: dict):
        if sender in self.user_feedback:
            self.user_feedback[sender].append(feedback)
        else:
            self.user_feedback[sender] = [feedback]

    def save_feedback(self, sender: str):
        feedback_data = self.user_feedback.get(sender, [])
        if feedback_data:
            feedback_file = f"{sender}_feedback.json"
            with open(feedback_file, "w") as f:
                json.dump(feedback_data, f, indent=4)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    language = await websocket.receive_text()
    if language not in {"English", "Hindi", "Spanish", "Persian"}:
        await websocket.close()
        return

    await manager.connect(websocket, language)

    try:
        while True:
            data = await websocket.receive_text()

            if data.startswith("{"):
                feedback_data = json.loads(data)
                print(f"feedback is given {data}")
                manager.add_feedback(feedback_data["sender"], feedback_data)
                manager.save_feedback(feedback_data["sender"])
            else:
                post_url = "http://localhost:8001/process"
                get_url = "http://localhost:8001/"
                headers = {'Content-Type': 'application/json'}
                team, text = data.split(": ")
                data = {"sender": team, "message": text}
                response = requests.post(post_url, data=json.dumps(data), headers=headers)
                response = requests.get(get_url)
                print(f"response from MT: {response.json()}")
                await manager.broadcast(team, response.json())
    except Exception as e:
        print(f"Exception: {e}")
        manager.disconnect(websocket)

# Serve static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")
