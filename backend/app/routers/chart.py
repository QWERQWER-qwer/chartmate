from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.services import vision_service

router = APIRouter(prefix="/api/chart", tags=["chart"])


@router.post("")
async def analyze_chart(image: UploadFile = File(...), note: str = Form("")):
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드할 수 있습니다.")
    data = await image.read()
    result = vision_service.analyze_chart(data, image.content_type, note)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result
