from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, AsyncGenerator
import json

from models.user import User
from services.auth_service import get_current_user
from services.chatbot_service import NutriChatbot

router = APIRouter()
chatbot = NutriChatbot()


class ChatMessage(BaseModel):
    message: str
    mood: Optional[str] = None
    context: Optional[dict] = None  # e.g., {"meal_type": "lunch", "location": "office"}


class ChatResponse(BaseModel):
    reply: str
    suggestions: list[str] = []
    action: Optional[str] = None  # "log_food", "show_recipe", "set_reminder"
    action_data: Optional[dict] = None


@router.post("/message", response_model=ChatResponse)
async def chat(
    data: ChatMessage,
    current_user: User = Depends(get_current_user),
):
    response = await chatbot.respond(
        user=current_user,
        message=data.message,
        mood=data.mood,
        context=data.context or {},
    )
    return response


@router.post("/message/stream")
async def chat_stream(
    data: ChatMessage,
    current_user: User = Depends(get_current_user),
):
    """Streaming chat response for real-time feel."""
    async def generate() -> AsyncGenerator[str, None]:
        async for chunk in chatbot.stream_respond(
            user=current_user,
            message=data.message,
            mood=data.mood,
            context=data.context or {},
        ):
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.websocket("/ws/{user_id}")
async def chat_websocket(websocket: WebSocket, user_id: str):
    """WebSocket for real-time chat."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")
            mood = data.get("mood")

            # Stream response chunks
            async for chunk in chatbot.stream_respond_simple(message, mood):
                await websocket.send_json({"chunk": chunk, "done": False})
            await websocket.send_json({"chunk": "", "done": True})

    except WebSocketDisconnect:
        pass


@router.get("/history")
async def get_chat_history(
    current_user: User = Depends(get_current_user),
    limit: int = 50,
):
    history = await chatbot.get_history(str(current_user.id), limit)
    return history


@router.delete("/history")
async def clear_chat_history(current_user: User = Depends(get_current_user)):
    await chatbot.clear_history(str(current_user.id))
    return {"message": "Chat history cleared"}
