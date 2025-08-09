from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from .connection_manager import connection_manager
from auth.services.login_service import LoginService
import json

router = APIRouter()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await connection_manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message["type"] == "subscribe_ride":
                ride_id = message["data"]["ride_id"]
                connection_manager.subscribe_to_ride(user_id, ride_id)
                await websocket.send_text(json.dumps({
                    "type": "subscribed",
                    "message": f"Subscribed to ride {ride_id}"
                }))
            
            elif message["type"] == "location_update":
                # Handle driver location updates
                await connection_manager.send_personal_message({
                    "type": "driver_location",
                    "data": message["data"]
                }, user_id)
                
    except WebSocketDisconnect:
        connection_manager.disconnect(user_id)