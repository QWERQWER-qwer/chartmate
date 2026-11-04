from fastapi import APIRouter, HTTPException
from app.models.schemas import DataIn, DataUpdate
from app.services import data_service

router = APIRouter(prefix="/api/data", tags=["data"])


@router.post("")
def create(item: DataIn):
    return data_service.create_data(item.model_dump())


@router.get("")
def list_all():
    return data_service.get_all_data()


@router.get("/summary")
def summary():
    return data_service.get_summary()


@router.put("/{doc_id}")
def update(doc_id: str, item: DataUpdate):
    fields = {k: v for k, v in item.model_dump().items() if v is not None}
    result = data_service.update_data(doc_id, fields)
    if result is None:
        raise HTTPException(status_code=404, detail="해당 데이터를 찾을 수 없습니다")
    return result


@router.delete("/{doc_id}")
def delete(doc_id: str):
    ok = data_service.delete_data(doc_id)
    if not ok:
        raise HTTPException(status_code=404, detail="해당 데이터를 찾을 수 없습니다")
    return {"message": "삭제 완료", "id": doc_id}