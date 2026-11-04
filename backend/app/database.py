import json
import firebase_admin
from firebase_admin import credentials, firestore
from app.config import FIREBASE_SERVICE_ACCOUNT_JSON, FIREBASE_KEY_PATH


def init_firestore():
    """Firebase 앱을 초기화하고 Firestore 클라이언트를 반환"""
    if not firebase_admin._apps:  # 이미 초기화됐으면 다시 안 함
        if FIREBASE_SERVICE_ACCOUNT_JSON:
            # 배포 환경: 환경변수에 담긴 JSON 문자열로 인증
            cred = credentials.Certificate(json.loads(FIREBASE_SERVICE_ACCOUNT_JSON))
        else:
            # 로컬 환경: 키 파일 경로로 인증
            cred = credentials.Certificate(FIREBASE_KEY_PATH)
        firebase_admin.initialize_app(cred)
    return firestore.client()


db = init_firestore()