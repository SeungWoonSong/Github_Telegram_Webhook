# GitHub Notifier Telegram Bot

GitHub 웹훅 이벤트를 Telegram으로 전송하는 봇입니다. 이슈, PR, 코드 리뷰 등 GitHub의 다양한 이벤트를 실시간으로 알림 받을 수 있습니다.

[English](#english)

## 기능

### 지원하는 GitHub 이벤트
1. **코드 관련**
   - Push
   - Create/Delete (브랜치, 태그)
   - Release
   - Package

2. **이슈 & PR**
   - Issues (생성, 수정, 닫기)
   - Issue Comments
   - Pull Requests
   - PR Reviews
   - PR Review Comments

3. **협업**
   - Discussions
   - Discussion Comments
   - Wiki Pages (Gollum)
   - Projects
   - Project Cards/Columns

4. **저장소 관리**
   - Fork
   - Star/Watch
   - Member
   - Team Add

5. **CI/CD**
   - Workflow Run/Job
   - Check Run/Suite
   - Deployment/Status

6. **보안**
   - Code Scanning Alert
   - Secret Scanning Alert
   - Dependabot Alert
   - Repository Vulnerability Alert

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
```env
# Telegram 봇 설정
TELEGRAM_BOT_TOKEN=your_bot_token        # Telegram Bot API 토큰
TELEGRAM_BOT_USERNAME=your_bot_username  # @ 기호를 제외한 봇 사용자명
TELEGRAM_DEFAULT_CHAT_ID=default_chat_id # 기본 채팅방 ID
TELEGRAM_WORK_CHAT_ID=your_work_chat_id  # 작업용 채팅방 ID

# 이벤트별 채팅방 매핑 (선택사항)
# 형식: {"이벤트_타입": "채팅방_ID"}
# 예시: {"issues,issue_comment": "-1001111111111", "push,pull_request": "-1002222222222"}
EVENT_CHAT_MAPPING={}

# 서버 설정
SERVER_PORT=8080       # 선택사항, 기본값: 8080
DEVELOPMENT_MODE=false # 개발 모드 여부 (true: 웹훅 없이 테스트)

# 서버 URL (선택사항)
# 설정하지 않으면 서버의 외부 IP를 사용
# 예시: your-domain.com 또는 subdomain.your-domain.com
SERVER_URL=
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

- 이슈 관련 알림은 `TELEGRAM_DEFAULT_CHAT_ID`로 전송됩니다.
- 개발 작업 관련 알림(PR, 리뷰, 푸시)은 `TELEGRAM_WORK_CHAT_ID`로 전송됩니다.
- 모든 환경 변수가 올바르게 설정되어 있는지 확인하세요.

---

# English

## Introduction
ChainChanger Bot is a bot that delivers GitHub repository events to Telegram chat rooms. It enables real-time notification of various GitHub events such as issues, PRs, and code reviews.

## Features

### Supported GitHub Events
1. **Code Related**
   - Push
   - Create/Delete (branches, tags)
   - Release
   - Package

2. **Issues & PRs**
   - Issues (creation, modification, closure)
   - Issue Comments
   - Pull Requests
   - PR Reviews
   - PR Review Comments

3. **Collaboration**
   - Discussions
   - Discussion Comments
   - Wiki Pages (Gollum)
   - Projects
   - Project Cards/Columns

4. **Repository Management**
   - Fork
   - Star/Watch
   - Member
   - Team Add

5. **CI/CD**
   - Workflow Run/Job
   - Check Run/Suite
   - Deployment/Status

6. **Security**
   - Code Scanning Alert
   - Secret Scanning Alert
   - Dependabot Alert
   - Repository Vulnerability Alert

## Configuration

### 1. Environment variable setup
Set the following variables in the `.env` file:
```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token        # Telegram Bot API token
TELEGRAM_BOT_USERNAME=your_bot_username  # Bot username without @ symbol
TELEGRAM_DEFAULT_CHAT_ID=default_chat_id # Default chat room ID
TELEGRAM_WORK_CHAT_ID=your_work_chat_id  # Work chat room ID

# Event-specific chat room mapping (optional)
# Format: {"event_type": "chat_id"}
# Example: {"issues,issue_comment": "-1001111111111", "push,pull_request": "-1002222222222"}
EVENT_CHAT_MAPPING={}

# Server Configuration
SERVER_PORT=8080       # Optional, default: 8080
DEVELOPMENT_MODE=false # Development mode flag

# Server URL (optional)
# External IP will be used if not set
# Example: your-domain.com or subdomain.your-domain.com
SERVER_URL=
```

### 2. GitHub Webhook setup
1. Go to GitHub repository's Settings > Webhooks
2. Click Add webhook
3. Enter the bot server address in the Payload URL
4. Set the Content type to `application/json`
5. Select the desired events:
   - Issues
   - Issue comments
   - Pull requests
   - Pull request reviews
   - Pushes

## Message format

All notifications are sent in the following consistent format:
```
[Emoji] *[Title]*
Repo: [Repository name]
Author/Reviewer: [User name]
Link: [Link]
```

## Running the bot

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python main.py
```

## Notes

- Issue-related notifications are sent to `TELEGRAM_DEFAULT_CHAT_ID`.
- Development work-related notifications (PR, review, push) are sent to `TELEGRAM_WORK_CHAT_ID`.
- Make sure all environment variables are set correctly.
