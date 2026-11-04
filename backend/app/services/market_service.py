"""시세·지표 조회 (AI Agent 툴)

ChartMate의 Agent가 호출하는 두 개의 도구:
- get_price      : 현재가 + 전일 대비 등락률
- get_indicators : 이동평균(60·200일), 모멘텀(126일), ATR(14) 변동성

지표 선정 근거: 과거 트레이딩 봇 작업에서 실제로 쓰고 유효성을 확인한
이동평균·모멘텀 + 변동성(ATR) 중심. (기획서 6장 참조)
"""
import pandas as pd
import yfinance as yf


def _download(ticker: str, period: str = "1y"):
    try:
        df = yf.Ticker(ticker).history(period=period)
    except Exception:
        return None
    if df is None or df.empty:
        return None
    return df


def get_price(ticker: str) -> dict:
    """현재가와 전일 대비 등락률(%)을 조회한다."""
    df = _download(ticker, period="5d")
    if df is None:
        return {"error": f"'{ticker}' 시세를 가져오지 못했습니다. 티커를 확인해 주세요."}
    close = df["Close"].dropna()
    if len(close) < 1:
        return {"error": f"'{ticker}' 가격 데이터가 없습니다."}
    last = float(close.iloc[-1])
    prev = float(close.iloc[-2]) if len(close) >= 2 else last
    change_pct = round((last - prev) / prev * 100, 2) if prev else 0.0
    return {"ticker": ticker.upper(), "price": round(last, 2), "change_pct": change_pct}


def _atr(df, period: int = 14):
    """ATR(평균 진폭) — 변동성 지표. NaN 행(오늘자 미완성 캔들 등)은 제외하고 계산."""
    sub = df[["High", "Low", "Close"]].dropna()
    if len(sub) < period + 1:
        return None
    high, low, close = sub["High"], sub["Low"], sub["Close"]
    prev_close = close.shift(1)
    tr = pd.concat(
        [(high - low), (high - prev_close).abs(), (low - prev_close).abs()], axis=1
    ).max(axis=1)
    atr = tr.rolling(period).mean().iloc[-1]
    return float(atr) if pd.notna(atr) else None


def get_indicators(ticker: str) -> dict:
    """이동평균(60·200일), 모멘텀(126일), ATR(14)을 계산한다."""
    df = _download(ticker, period="1y")
    if df is None:
        return {"error": f"'{ticker}' 데이터를 가져오지 못했습니다. 티커를 확인해 주세요."}
    close = df["Close"].dropna()
    if len(close) < 2:
        return {"error": f"'{ticker}' 데이터가 부족합니다."}

    last = float(close.iloc[-1])
    result = {"ticker": ticker.upper(), "price": round(last, 2)}

    # 이동평균선 — 현재가가 추세선 위/아래 어디인지
    if len(close) >= 60:
        ma60 = float(close.rolling(60).mean().iloc[-1])
        result["ma60"] = round(ma60, 2)
        result["vs_ma60"] = "위" if last >= ma60 else "아래"
    if len(close) >= 200:
        ma200 = float(close.rolling(200).mean().iloc[-1])
        result["ma200"] = round(ma200, 2)
        result["vs_ma200"] = "위" if last >= ma200 else "아래"

    # 모멘텀 126일 — 반년 수익률(%)
    if len(close) >= 127:
        past = float(close.iloc[-127])
        result["momentum_126d_pct"] = round((last - past) / past * 100, 2) if past else None

    # ATR(14) — 변동성(절대값 + 가격 대비 %)
    atr = _atr(df, 14)
    if atr is not None:
        result["atr14"] = round(atr, 2)
        result["atr14_pct"] = round(atr / last * 100, 2) if last else None

    return result
