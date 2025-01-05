# ChainChanger Bot

GitHub 웹훅 이벤트를 Telegram으로 전송하는 봇입니다. 이슈, PR, 코드 리뷰 등 GitHub의 다양한 이벤트를 실시간으로 알림 받을 수 있습니다.

## 기능

### 1. Issue 관련 알림 (일반 채팅방)
- 이슈 생성 🟢
- 이슈 닫기 🔴
- 이슈 재열기 🔄
- 이슈 삭제 🗑️
- 이슈 댓글 🗣️

### 2. 개발 작업 관련 알림 (작업용 채팅방)
#### Pull Request
- PR 생성 💫
- PR 닫기 🔒
- PR 재열기 🔄

#### Code Review
- 일반 코멘트 💭
- 승인 ✅
- 변경 요청 ❌
- 리뷰 철회 🔄

#### Push
- 코드 푸시 📦

## 설정 방법

### 1. 환경 변수 설정
`.env` 파일에 다음 변수들을 설정해야 합니다:
```
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
TELEGRAM_WORK_CHAT_ID=your_work_chat_id
```

### 2. GitHub Webhook 설정
1. GitHub 저장소의 Settings > Webhooks로 이동
2. Add webhook 클릭
3. Payload URL에 봇 서버 주소 입력
4. Content type을 `application/json`으로 설정
5. 원하는 이벤트 선택:
   - Issues
   - Issue comments
   - Pull requests
   - Pull request reviews
   - Pushes

## 메시지 포맷

모든 알림은 다음과 같은 일관된 포맷으로 전송됩니다:
```
[이모지] *[제목]*
레포 : [저장소 이름]
작성자/리뷰어 : [사용자 이름]
링크 : [링크]
```

## 실행 방법

1. 의존성 설치:
```bash
pip install -r requirements.txt
```

2. 서버 실행:
```bash
python main.py
```

## 주의사항

- 이슈 관련 알림은 `TELEGRAM_CHAT_ID`로 전송됩니다.
- 개발 작업 관련 알림(PR, 리뷰, 푸시)은 `TELEGRAM_WORK_CHAT_ID`로 전송됩니다.
- 모든 환경 변수가 올바르게 설정되어 있는지 확인하세요.
