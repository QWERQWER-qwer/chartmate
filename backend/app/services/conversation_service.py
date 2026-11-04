from datetime import datetime, timezone
from firebase_admin import firestore
from app.database import db

COLLECTION = "conversations"


def create_conversation(data: dict) -> dict:
    """대화 저장 (생성 시각 자동 기록)"""
    data["created_at"] = datetime.now(timezone.utc).isoformat()
    doc_ref = db.collection(COLLECTION).document()
    doc_ref.set(data)
    return {"id": doc_ref.id, **data}


def get_all_conversations() -> list:
    """대화 목록 조회 (최신순)"""
    docs = (
        db.collection(COLLECTION)
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .stream()
    )
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]


def get_conversation(doc_id: str):
    """특정 대화 전체 불러오기 (없으면 None)"""
    doc = db.collection(COLLECTION).document(doc_id).get()
    if not doc.exists:
        return None
    return {"id": doc.id, **doc.to_dict()}


def delete_conversation(doc_id: str) -> bool:
    """대화 삭제 (없으면 False)"""
    doc_ref = db.collection(COLLECTION).document(doc_id)
    if not doc_ref.get().exists:
        return False
    doc_ref.delete()
    return True