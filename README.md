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

## 설정 방법

1. Telegram Bot Father(@BotFather)에게 문의해서 TELEGRAM_BOT_TOKEN 발급 받기

2. 발급받을 때 사용한 이름 TELEGRAM_BOT_USERNAME, 그리고 발급 받은 TELEGRAM_BOT_TOKEN을 .env에 넣기

3. `pip3 install -r requirements.txt`로 실행시킨 후, 이슈를 받아오기를 희망하는 채팅방에 봇을 초대 후 `/get_chat_id` 이용해서 chat id 받아오기

4. 받아온 chat id를 .env의 TELEGRAM_DEFAULT_CHAT_ID에 설정하기

5. 만약 특정 이벤트는 다른 방으로 받고 싶다면 해당 방을 EVENT_CHAT_MAPPING에 매핑해두기

6. 서버 재시작

7. 필요시 테스트 파일을 이용해 테스트 진행하기 

### GitHub Webhook 설정
1. GitHub 저장소의 Settings > Webhooks로 이동
2. Add webhook 클릭
3. Payload URL에 `https://<your_domain or IP address>/webhook` 입력
4. Content type을 `application/json`으로 설정
5. 원하는 이벤트 선택 후 저장

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

- 기본적인 알림은 `TELEGRAM_DEFAULT_CHAT_ID`로 전송됩니다.
- 매핑된 알람은 `EVENT_CHAT_MAPPING`에 매핑되어 있는 채팅방으로 전송됩니다.
- 모든 환경 변수가 올바르게 설정되어 있는지 확인하세요.

---

# English

A bot that delivers GitHub webhook events to Telegram. You can receive real-time notifications for various GitHub events such as issues, PRs, and code reviews.

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

## Setup Instructions

1. Get TELEGRAM_BOT_TOKEN from Telegram Bot Father (@BotFather)

2. Add the bot name used during creation as TELEGRAM_BOT_USERNAME and the received TELEGRAM_BOT_TOKEN to .env

3. Run `pip3 install -r requirements.txt`, invite the bot to the chat room where you want to receive issues, and use `/get_chat_id` to get the chat id

4. Set the received chat id in TELEGRAM_DEFAULT_CHAT_ID in .env

5. If you want to receive specific events in different rooms, map them in EVENT_CHAT_MAPPING

6. Restart the server

7. Run tests using the test files if needed

### GitHub Webhook Setup
1. Go to GitHub repository's Settings > Webhooks
2. Click Add webhook
3. Enter `https://<your_domain or IP address>/webhook` as Payload URL
4. Set Content type to `application/json`
5. Select desired events and save

## Message Format

All notifications are sent in the following consistent format:
```
[Emoji] *[Title]*
Repo: [Repository name]
Author/Reviewer: [User name]
Link: [Link]
```

## How to Run

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python main.py
```

## Notes

- Basic notifications are sent to `TELEGRAM_DEFAULT_CHAT_ID`
- Mapped notifications are sent to chat rooms specified in `EVENT_CHAT_MAPPING`
- Make sure all environment variables are set correctly
