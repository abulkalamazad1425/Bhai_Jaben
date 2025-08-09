from typing import Dict, List
from fastapi import WebSocket
import json
from datetime import datetime

class ConnectionManager:
    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[str, WebSocket] = {}
        # Store connections by ride_id for ride-specific updates
        self.ride_connections: Dict[str, List[str]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        # Remove from ride connections
        for ride_id, users in self.ride_connections.items():
            if user_id in users:
                users.remove(user_id)
    
    def subscribe_to_ride(self, user_id: str, ride_id: str):
        if ride_id not in self.ride_connections:
            self.ride_connections[ride_id] = []
        if user_id not in self.ride_connections[ride_id]:
            self.ride_connections[ride_id].append(user_id)
    
    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            await websocket.send_text(json.dumps({
                **message,
                "timestamp": datetime.now().isoformat()
            }))
    
    async def send_ride_update(self, ride_id: str, message: dict):
        if ride_id in self.ride_connections:
            for user_id in self.ride_connections[ride_id]:
                await self.send_personal_message(message, user_id)
    
    async def broadcast_to_drivers(self, message: dict, driver_ids: List[str]):
        for driver_id in driver_ids:
            await self.send_personal_message(message, driver_id)

# Global connection manager instance
connection_manager = ConnectionManager()