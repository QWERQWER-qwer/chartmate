"""차트 이미지 해석 (멀티모달) — Google Gemini

코디세이 OpenAI 엔드포인트가 이미지 입력을 지원하지 않아, 차트 해석은
Gemini 비전(gemini-3.5-flash)으로 처리한다.

[배포 안정화] google-genai는 무겁다(grpc 등). 서버 시작 시 전부 불러오면
무료 인스턴스(512MB)에서 startup이 막힐 수 있어, import·클라이언트 생성을
'첫 차트 요청 때'로 미루는 지연 로딩(lazy)으로 둔다.
"""
import time

from app.config import GEMINI_API_KEY

MODEL = "gemini-3.5-flash"

VISION_PROMPT = (
    "당신은 투자 초보를 돕는 AI 투자 비서 'ChartMate'입니다.\n"
    "업로드된 '주가 차트 이미지'를 보고 아래를 관찰해 쉬운 말로 설명하세요. "
    "미래 예측이나 매수/매도 권유는 하지 않습니다.\n"
    "- 전반적 추세: 상승 / 하락 / 횡보 중 무엇으로 보이는지\n"
    "- 지지/저항: 눈에 띄는 구간이 있으면 한 줄\n"
    "- 특징: 최근 변동성·패턴에서 보이는 점\n"
    "짧은 브리핑 형식으로 답하세요. 차트가 아닌 이미지면 "
    "'차트 이미지로 보이지 않아요'라고만 답하세요.\n"
    "끝에 항상 '※ 투자 참고용 정보이며 매수·매도 권유가 아닙니다.'를 붙입니다."
)

_client = None


def _get_client():
    """Gemini 클라이언트를 처음 쓸 때 한 번만 생성 (지연 로딩)."""
    global _client
    if _client is None:
        if not GEMINI_API_KEY:
            return None
        from google import genai  # 지연 import
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def analyze_chart(image_bytes: bytes, mime_type: str = "image/png", user_note: str = "") -> dict:
    client = _get_client()
    if client is None:
        return {"error": "GEMINI_API_KEY가 설정되지 않았습니다. 환경변수를 확인하세요."}

    from google.genai import types  # 지연 import

    text = VISION_PROMPT + (f"\n\n사용자 메모: {user_note}" if user_note else "")
    last_err = None
    for attempt in range(3):
        try:
            resp = client.models.generate_content(
                model=MODEL,
                contents=[
                    text,
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                ],
            )
            return {"analysis": resp.text}
        except Exception as e:
            last_err = e
            msg = str(e)
            if "503" in msg or "UNAVAILABLE" in msg or "high demand" in msg:
                time.sleep(2 * (attempt + 1))
                continue
            return {"error": f"차트 분석 실패: {e}"}
    return {"error": "차트 분석 서버가 잠시 혼잡해요. 잠시 후 다시 시도해 주세요."}
