"""
WebSocket stream endpoint for real-time data streaming.
"""

import json
import asyncio
from typing import Dict, Any, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
import structlog

logger = structlog.get_logger()

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections and broadcasts messages."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str = None):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if client_id:
            logger.info("New WebSocket connection", client_id=client_id)
        else:
            logger.info("New WebSocket connection")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from all subscriptions
        for topic, connections in self.subscriptions.items():
            if websocket in connections:
                connections.remove(websocket)
        
        logger.info("WebSocket connection closed")
    
    async def subscribe(self, websocket: WebSocket, topic: str):
        """Subscribe a connection to a specific topic."""
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []
        
        if websocket not in self.subscriptions[topic]:
            self.subscriptions[topic].append(websocket)
            logger.info("Client subscribed to topic", topic=topic)
    
    async def unsubscribe(self, websocket: WebSocket, topic: str):
        """Unsubscribe a connection from a specific topic."""
        if topic in self.subscriptions and websocket in self.subscriptions[topic]:
            self.subscriptions[topic].remove(websocket)
            logger.info("Client unsubscribed from topic", topic=topic)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error("Failed to send personal message", error=str(e))
            self.disconnect(websocket)
    
    async def broadcast(self, message: str, topic: str = None):
        """Broadcast a message to all connections or topic subscribers."""
        if topic and topic in self.subscriptions:
            # Send to topic subscribers
            disconnected = []
            for connection in self.subscriptions[topic]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error("Failed to broadcast to topic subscriber", error=str(e))
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for connection in disconnected:
                self.disconnect(connection)
        else:
            # Send to all active connections
            disconnected = []
            for connection in self.active_connections:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error("Failed to broadcast message", error=str(e))
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for connection in disconnected:
                self.disconnect(connection)


# Global connection manager
manager = ConnectionManager()


@router.get("/")
async def get_websocket_info():
    """Get WebSocket connection information."""
    return {
        "active_connections": len(manager.active_connections),
        "topics": list(manager.subscriptions.keys()),
        "subscription_counts": {
            topic: len(connections) 
            for topic, connections in manager.subscriptions.items()
        }
    }


@router.websocket("/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Main WebSocket endpoint for real-time data streaming."""
    await manager.connect(websocket, client_id)
    
    try:
        # Send welcome message
        welcome_message = {
            "type": "connection_established",
            "client_id": client_id,
            "message": "Connected to KashRock Data Stream",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        await manager.send_personal_message(
            json.dumps(welcome_message), 
            websocket
        )
        
        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                await handle_websocket_message(websocket, message, client_id)
                
            except json.JSONDecodeError:
                error_message = {
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
                await manager.send_personal_message(
                    json.dumps(error_message), 
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error("WebSocket error", error=str(e), client_id=client_id)
        manager.disconnect(websocket)


async def handle_websocket_message(websocket: WebSocket, message: Dict[str, Any], client_id: str):
    """Handle incoming WebSocket messages."""
    message_type = message.get("type")
    
    if message_type == "subscribe":
        topic = message.get("topic")
        if topic:
            await manager.subscribe(websocket, topic)
            response = {
                "type": "subscription_confirmed",
                "topic": topic,
                "message": f"Subscribed to {topic}",
                "timestamp": "2024-01-01T00:00:00Z"
            }
            await manager.send_personal_message(json.dumps(response), websocket)
    
    elif message_type == "unsubscribe":
        topic = message.get("topic")
        if topic:
            await manager.unsubscribe(websocket, topic)
            response = {
                "type": "unsubscription_confirmed",
                "topic": topic,
                "message": f"Unsubscribed from {topic}",
                "timestamp": "2024-01-01T00:00:00Z"
            }
            await manager.send_personal_message(json.dumps(response), websocket)
    
    elif message_type == "ping":
        response = {
            "type": "pong",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        await manager.send_personal_message(json.dumps(response), websocket)
    
    else:
        # Echo back unknown message types
        response = {
            "type": "echo",
            "original_message": message,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        await manager.send_personal_message(json.dumps(response), websocket)


# Example function to broadcast data updates
async def broadcast_odds_update(sport: str, game_id: str, odds_data: Dict[str, Any]):
    """Broadcast odds update to subscribers."""
    message = {
        "type": "odds_update",
        "sport": sport,
        "game_id": game_id,
        "data": odds_data,
        "timestamp": "2024-01-01T00:00:00Z"
    }
    
    topic = f"odds_{sport}"
    await manager.broadcast(json.dumps(message), topic)


# Example function to broadcast game status updates
async def broadcast_game_status(sport: str, game_id: str, status_data: Dict[str, Any]):
    """Broadcast game status update to subscribers."""
    message = {
        "type": "game_status",
        "sport": sport,
        "game_id": game_id,
        "data": status_data,
        "timestamp": "2024-01-01T00:00:00Z"
    }
    
    topic = f"game_{sport}"
    await manager.broadcast(json.dumps(message), topic)
