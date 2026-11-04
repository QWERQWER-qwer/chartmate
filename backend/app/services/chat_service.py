"""ChartMate 챗 서비스 — OpenAI 대화 + AI Agent(수동 라우터 방식)

[설계 결정] 지정된 코디세이 엔드포인트(gpt-5-mini)가 function calling(tools)을
지원하지 않아(400 unsupported_feature), tools API 대신 '종목 인식 → 도구 호출 →
결과 주입' 2단계로 Agent를 구현한다.
  1) 종목 인식: 사전(한글명→티커) 우선, 실패 시 모델 라우터로 추출
  2) 도구 실행: get_price / get_indicators 호출
  3) 답변 생성: 조회 결과를 주입해 '짧은 브리핑'으로 응답
"""
import json
import re

from openai import OpenAI

from app.config import OPENAI_API_KEY, OPENAI_BASE_URL
from app.services import market_service
from app.services.conversation_service import create_conversation

if OPENAI_BASE_URL:
    client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
else:
    client = OpenAI(api_key=OPENAI_API_KEY)

MODEL = "gpt-5-mini"

# 자주 쓰는 한글 종목명 → 티커 (빠르고 확실한 1차 인식)
NAME_TO_TICKER = {
    "엔비디아": "NVDA", "애플": "AAPL", "테슬라": "TSLA", "마이크로소프트": "MSFT",
    "구글": "GOOGL", "알파벳": "GOOGL", "아마존": "AMZN", "메타": "META",
    "넷플릭스": "NFLX", "브로드컴": "AVGO", "마이크론": "MU", "팔란티어": "PLTR",
    "AMD": "AMD", "인텔": "INTC", "비트코인": "BTC-USD", "이더리움": "ETH-USD",
    "삼성전자": "005930.KS", "SK하이닉스": "000660.KS",
}
_STOP = {"AI", "RSI", "ATR", "ETF", "USD", "PER", "CEO", "API", "GPT", "ChartMate".upper()}


def _detect_ticker(message: str):
    """사전 + 간단 규칙으로 티커를 먼저 찾는다. (모델 호출 없이)"""
    for name, tk in NAME_TO_TICKER.items():
        if name.lower() in message.lower():
            return tk
    # 메시지에 대문자 티커가 직접 들어온 경우 (예: NVDA)
    for tok in re.findall(r"\b[A-Z]{2,5}\b", message):
        if tok not in _STOP:
            return tok
    return None


def _plan_with_model(message: str):
    """[폴백] 사전에서 못 찾으면 모델에게 티커를 물어본다. (JSON만 유도)"""
    prompt = (
        "다음 메시지가 특정 주식/ETF/크립토의 시세·지표를 묻는지 판단해 JSON으로만 답하라.\n"
        '형식: {"need": true/false, "ticker": "야후파이낸스 티커 또는 null"}\n'
        "한글 종목명은 티커로 변환(예: 엔비디아→NVDA). 시세와 무관하면 need=false.\n"
        f"메시지: {message}"
    )
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=60,
        )
        text = resp.choices[0].message.content or ""
        s, e = text.find("{"), text.rfind("}")
        plan = json.loads(text[s:e + 1]) if s >= 0 and e > s else {}
        if plan.get("need") and plan.get("ticker"):
            return plan["ticker"]
    except Exception:
        pass
    return None


SYSTEM_PROMPT = (
    "당신은 투자 초보를 돕는 AI 투자 비서 'ChartMate'입니다.\n"
    "종목 데이터가 주어지면 반드시 아래 '브리핑 형식'으로 짧고 명확하게 답하세요. "
    "장황한 일반론·교과서식 나열은 금지합니다.\n\n"
    "[브리핑 형식]\n"
    "{종목} 브리핑\n"
    "· 현재가: $가격 (전일 대비 ±%)\n"
    "· 추세: 60일선/200일선 대비 위/아래 — 한 줄 해석\n"
    "· 변동성: ATR 기준 높음/보통/낮음\n"
    "· 모멘텀(126일): ±% — 한 줄 해석\n"
    "· 요약: 1~2문장\n\n"
    "규칙:\n"
    "- 주어진 수치만 사용하고 추측하지 않습니다.\n"
    "- 데이터에 error가 있으면 '해당 종목 데이터를 가져오지 못했어요'라고만 답합니다.\n"
    "- 종목 데이터가 없는 일반 질문이면 2~3문장으로 짧게 답합니다.\n"
    "- 끝에 항상 '※ 투자 참고용 정보이며 매수·매도 권유가 아닙니다.'를 붙입니다.\n"
    "- 매수/매도를 지시하거나 권유하지 않습니다."
)


def chat(user_message: str, history: list) -> dict:
    # 1) 종목 인식 (사전 → 모델 폴백)
    ticker = _detect_ticker(user_message) or _plan_with_model(user_message)

    # 2) 도구 실행
    market_context = ""
    if ticker:
        collected = {
            "price": market_service.get_price(ticker),
            "indicators": market_service.get_indicators(ticker),
        }
        market_context = json.dumps(collected, ensure_ascii=False)

    # 3) 답변 생성
    system_prompt = SYSTEM_PROMPT
    if market_context:
        system_prompt += f"\n\n[조회된 실시간 데이터]\n{market_context}"

    messages = [{"role": "system", "content": system_prompt}]
    messages += history
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_completion_tokens=1200,
    )
    answer = response.choices[0].message.content

    # 4) 대화 저장
    saved_messages = history + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": answer},
    ]
    conv = create_conversation({"title": user_message[:20], "messages": saved_messages})

    return {"answer": answer, "conversation_id": conv["id"], "ticker": ticker}
