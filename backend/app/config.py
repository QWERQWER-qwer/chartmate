import os
from dotenv import load_dotenv

load_dotenv()  # .env 파일을 읽어 환경변수로 로드

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
FIREBASE_SERVICE_ACCOUNT_JSON = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "")
FIREBASE_KEY_PATH = os.getenv("FIREBASE_KEY_PATH", "serviceAccountKey.json")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")