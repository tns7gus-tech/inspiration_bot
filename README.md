# 💡 영감봇 (Inspiration Bot)

매일 아침 09:00에 창의적인 프로젝트 아이디어를 텔레그램으로 보내주는 봇

## 🚀 빠른 시작

### 1. 환경 설정
```bash
cp .env.example .env
# .env 파일 편집하여 실제 값 입력
```

### 2. 필수 환경변수
- `TELEGRAM_BOT_TOKEN`: 텔레그램 봇 토큰
- `TELEGRAM_CHAT_ID`: 메시지 받을 채팅 ID
- `GEMINI_API_KEY`: Google Gemini API 키 ([발급받기](https://aistudio.google.com/apikey))

### 3. 로컬 실행
```bash
pip install -r requirements.txt
python main.py
```

### 4. 테스트 (즉시 발송)
```bash
python main.py --test
```

## 🚂 Railway 배포

1. GitHub에 푸시
2. Railway에서 새 프로젝트 생성
3. 환경변수 설정 (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, GEMINI_API_KEY)
4. 자동 배포!

## 📁 파일 구조

```
inspiration_bot/
├── main.py              # 메인 스케줄러
├── idea_generator.py    # Gemini AI 아이디어 생성
├── idea_summary_store.py# 아이디어 요약 파일 관리
├── idea_summaries.txt   # 기존 아이디어 요약 목록(중복/유사 방지용)
├── telegram_notifier.py # 텔레그램 발송
├── config.py            # 설정 관리
├── requirements.txt     # 의존성
├── railway.json         # Railway 배포 설정
└── .env.example         # 환경변수 예시
```

## ⏰ 발송 시간 변경

`.env` 파일에서 수정:
```
SEND_HOUR=9
SEND_MINUTE=0
```

## 🧠 중복/유사 아이디어 방지

- 매일 발송 전 `idea_summaries.txt`를 읽어 기존 아이디어를 프롬프트에 반영합니다.
- 새 아이디어가 생성되면 핵심 내용이 한 줄 요약으로 `idea_summaries.txt`에 자동 추가됩니다.
- 생성 후 Gemini 검색 기반 검증을 한 번 더 수행하여 이미 널리 존재하는 서비스와 유사하면 재생성합니다.
