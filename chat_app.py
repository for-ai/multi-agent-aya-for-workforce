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
        self.user_languages: Dict[int, str] = {}  # Track languages by websocket ID
        self.usernames: Dict[int, str] = {}  # Track usernames by websocket ID
        self.user_feedback: Dict[str, List[Dict]] = {}

        self.language_to_team = {
            'English': 'TeamA',
            'Hindi': 'TeamB',
            'Spanish': 'TeamC',
            'Persian': 'TeamD'
        }

    async def connect(self, websocket: WebSocket, username: str, language: str):
        self.active_connections.append(websocket)
        websocket_id = id(websocket)
        self.connection_modes[websocket_id] = language
        self.user_languages[websocket_id] = language
        self.usernames[websocket_id] = username
        await self.broadcast_user_list()  # Broadcast updated user list

    async def disconnect(self, websocket: WebSocket):
        websocket_id = id(websocket)
        self.active_connections.remove(websocket)
        del self.connection_modes[websocket_id]
        del self.user_languages[websocket_id]
        del self.usernames[websocket_id]
        await self.broadcast_user_list()  # Broadcast updated user list

    async def broadcast(self, sender: str, translator_message: dict):
        for connection in self.active_connections:
            team_name = self.language_to_team.get(self.connection_modes[id(connection)])
            team_message = translator_message.get(team_name)
            await connection.send_text(json.dumps({"sender": sender, "message": team_message}))

    async def broadcast_user_list(self):
        users = [{"username": self.usernames[id(ws)], "language": self.user_languages[id(ws)]}
                 for ws in self.active_connections]
        user_list_message = {"type": "user_list", "users": users}
        for connection in self.active_connections:
            await connection.send_text(json.dumps(user_list_message))

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
    language = await websocket.receive_text()  # First message is the language
    username = await websocket.receive_text()  # Second message is the username

    if language not in {"English", "Hindi", "Spanish", "Persian"} or not username:
        await websocket.close()
        return

    await manager.connect(websocket, username, language)

    try:
        while True:
            data = await websocket.receive_text()

            if data.startswith("{"):
                feedback_data = json.loads(data)
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
                await manager.broadcast(team, response.json())
    except Exception as e:
        print(f"Exception: {e}")
        await manager.disconnect(websocket)  # Await disconnect as it is now async

# Serve static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

