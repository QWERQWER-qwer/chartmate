from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import ALLOWED_ORIGINS
from app.routers import data, conversations, chat

app = FastAPI(title="데이터 AI 비서 API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 연결
app.include_router(data.router)
app.include_router(conversations.router)
app.include_router(chat.router)


@app.get("/")
def root():
    return {"message": "데이터 AI 비서 API 서버가 실행 중입니다."}


@app.get("/health")
def health():
    return {"status": "ok"}