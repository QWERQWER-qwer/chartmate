from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatIn
from app.services import chat_service

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("")
def chat(body: ChatIn):
    try:
        history = [m.model_dump() for m in body.history]
        return chat_service.chat(body.message, history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 응답 생성 실패: {e}")