# ChartMate

> 차트 해석과 지표 조회를 대화 한 번으로 대신 해주는, 투자 초보용 AI 투자 비서.

## 실행 방법

### 요구사항
- Python 3.10+
- (프론트는 정적 파일이라 별도 빌드 불필요)

### 설치 및 실행
```bash
git clone https://github.com/QWERQWER-qwer/chartmate.git
cd chartmate

# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload   # http://localhost:8000/docs

# Frontend
cd ../frontend
# index.html을 브라우저로 열거나, 배포본(Vercel) URL 사용
```

### 환경 변수 (backend/.env)
```
OPENAI_API_KEY=...
GEMINI_API_KEY=...
# Firebase 서비스 계정 키 경로 등
```

## 링크
- 배포 URL: (배포 후 기입)
- 발표 자료: /docs/presentation.pdf
- 시연 영상: (업로드 후 기입)

## 프로젝트 소개

투자 초보가 겪는 ① 차트를 봐도 해석하기 어렵고, ② 종목마다 지표를 매번 찾아보기 번거로운 문제를 대화형으로 해소하는 AI 투자 비서. 실시간 시세·지표 조회(AI Agent), 차트 이미지 해석(멀티모달), 관심종목·대화 맥락 유지(Long-term Memory)를 제공한다.

(자세한 문제 정의·설계 근거는 [기획서](docs/기획서.md) 참조)

## 팀원 및 역할

| 이름 | 역할 | 담당 업무 |
|------|------|-----------|
| 전민재 | PM / Backend | 기획·문서 총괄, AI Agent·멀티모달 백엔드, 배포 |
| (B) | Frontend | 차트 업로드 UI·고지 배너, 발표자료 |
| (C) | Test / Docs | 실사용자 테스트 운영, 윤리·개인정보 문구, 피드백 정리 |

## 기술 스택

- **AI**: OpenAI API(대화), Google Gemini(차트 이미지 해석)
- **Backend**: FastAPI, Render
- **Frontend**: HTML / CSS / JavaScript, Vercel
- **DB**: Firebase Firestore
- **데이터**: yfinance (시세·지표)

## 핵심 AI 활용

- **AI Agent**: `get_price`·`get_indicators` 툴을 function calling으로 호출해 현재가·이동평균(60·200일)·모멘텀(126일)·ATR을 조회·해석
- **멀티모달**: 차트 이미지를 Gemini 비전으로 읽어 추세·주요 구간 설명
- **Long-term Memory**: 사용자별 관심종목·대화 기록을 Firestore에 저장·로드

## 사용자 테스트 결과

(C 작성 — 테스터 수, 주요 피드백 및 반영 사항)

## 협업 과정

(C 작성 — 커뮤니케이션 방식, 미팅 기록, 역할 수행)

## 한계

- 비공식 시세 API(yfinance) 사용 — 실시간성·정확성 보장 안 됨 (미구현 보완 과제)
- 차트 해석은 비전 모델의 '관찰'이며 미래 예측이 아님
- 본 서비스는 투자 참고용이며 투자자문·매매 권유가 아님
