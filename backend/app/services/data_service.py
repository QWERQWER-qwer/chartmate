"""데이터 CRUD + 요약 (Firestore)

원본 미션의 데이터 기능을 유지하되, 일회성 분석 스크립트(analyze.py) 의존을
제거하고 요약을 Firestore 데이터로 자체 계산한다.
"""
from app.database import db

COLLECTION = "data"


def create_data(item: dict) -> dict:
    """새 데이터 추가 (자동 ID 생성)"""
    doc_ref = db.collection(COLLECTION).document()
    doc_ref.set(item)
    return {"id": doc_ref.id, **item}


def get_all_data() -> list:
    """전체 데이터 목록 조회 (날짜순 정렬)"""
    docs = db.collection(COLLECTION).order_by("date").stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]


def update_data(doc_id: str, fields: dict):
    """데이터 수정 (없으면 None 반환)"""
    doc_ref = db.collection(COLLECTION).document(doc_id)
    if not doc_ref.get().exists:
        return None
    doc_ref.update(fields)
    updated = doc_ref.get()
    return {"id": updated.id, **updated.to_dict()}


def delete_data(doc_id: str) -> bool:
    """데이터 삭제 (없으면 False 반환)"""
    doc_ref = db.collection(COLLECTION).document(doc_id)
    if not doc_ref.get().exists:
        return False
    doc_ref.delete()
    return True


def get_summary() -> dict:
    """전체 데이터를 요약해서 반환 (기간·건수·주요 지표·트렌드)"""
    data = get_all_data()
    if not data:
        return {"period": None, "count": 0, "metrics": {}, "trend": None}

    values = [d.get("value") for d in data if isinstance(d.get("value"), (int, float))]
    dates = [d.get("date") for d in data if d.get("date")]

    metrics = {}
    if values:
        metrics = {
            "min": round(min(values), 2),
            "max": round(max(values), 2),
            "avg": round(sum(values) / len(values), 2),
            "latest": round(values[-1], 2),
        }

    trend = None
    if len(values) >= 2:
        if values[-1] > values[0]:
            trend = "상승"
        elif values[-1] < values[0]:
            trend = "하락"
        else:
            trend = "보합"

    period = f"{min(dates)} ~ {max(dates)}" if dates else None

    return {"period": period, "count": len(data), "metrics": metrics, "trend": trend}
