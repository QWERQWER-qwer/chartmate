from fastapi import APIRouter, HTTPException
from app.models.schemas import ConversationIn
from app.services import conversation_service

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.post("")
def create(conv: ConversationIn):
    return conversation_service.create_conversation(conv.model_dump())


@router.get("")
def list_all():
    return conversation_service.get_all_conversations()


@router.get("/{doc_id}")
def get_one(doc_id: str):
    result = conversation_service.get_conversation(doc_id)
    if result is None:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다")
    return result


@router.delete("/{doc_id}")
def delete(doc_id: str):
    ok = conversation_service.delete_conversation(doc_id)
    if not ok:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다")
    return {"message": "삭제 완료", "id": doc_id}