from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import os

# .env 파일에서 환경변수 로드
load_dotenv()

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # 수신할 채팅방 ID (봇과 대화 후 @get_id_bot 사용 가능)

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("환경변수 TELEGRAM_BOT_TOKEN과 TELEGRAM_CHAT_ID가 설정되어 있지 않습니다.")


def parse_push_event(data):
    """
    Push 이벤트 메시지 생성
    
    표시 정보:
    - 레포지토리 이름
    - Push 한 사용자
    - 첫 번째 커밋 내용
    - 추가 커밋 수 (있는 경우)
    """
    repository = data.get('repository', {})
    pusher = data.get('pusher', {})
    commits = data.get('commits', [])

    repo_name = repository.get('full_name', '알 수 없음')
    pusher_name = pusher.get('name', '알 수 없음')

    # 첫 번째 커밋만 표시
    if commits:
        first_commit = commits[0]
        commit_message = first_commit.get('message', '')
        commit_url = first_commit.get('url', '')
        commit_info = f"[커밋 보기]({commit_url})"
        remaining = len(commits) - 1
        remaining_info = f"\n추가 커밋 {remaining}개" if remaining > 0 else ""
    else:
        commit_message = "커밋 없음"
        commit_info = ""
        remaining_info = ""

    parsed_message = (
        f"🔄 *Push*\n"
        f"*{repo_name}*\n"
        f"by {pusher_name}\n"
        f"{commit_message}\n"
        f"{commit_info}{remaining_info}"
    )

    return parsed_message


def parse_pull_request_event(data):
    """
    Pull Request 이벤트 메시지 생성
    
    지원하는 액션:
    - opened: PR 생성 🟢
    - closed: PR 닫힘 🔴
    - reopened: PR 재오픈 🔄
    
    표시 정보:
    - PR 번호
    - 레포지토리 이름
    - PR 제목
    - 작성자
    """
    action = data.get('action', '')
    pr = data.get('pull_request', {})
    
    if action not in ['opened', 'closed', 'reopened']:
        return None
        
    repo = data.get('repository', {})
    repo_name = repo.get('full_name', '알 수 없음')
    pr_number = pr.get('number', '?')
    title = pr.get('title', '제목 없음')
    user = pr.get('user', {}).get('login', '알 수 없음')
    html_url = pr.get('html_url', '')

    action_emoji = {
        'opened': '🟢',
        'closed': '🔴',
        'reopened': '🔄'
    }.get(action, '')

    parsed_message = (
        f"{action_emoji} *PR #{pr_number}*\n"
        f"*{repo_name}*\n"
        f"{title}\n"
        f"by {user}\n"
        f"[PR 보기]({html_url})"
    )

    return parsed_message


def parse_issues_event(data):
    """
    Issue 이벤트 메시지 생성
    
    지원하는 액션:
    - opened: 이슈 생성 🟢
    - closed: 이슈 닫힘 🔴
    - reopened: 이슈 재오픈 🔄
    
    표시 정보:
    - 이슈 번호
    - 레포지토리 이름
    - 이슈 제목
    - 작성자
    """
    action = data.get('action', '')
    if action not in ['opened', 'closed', 'reopened']:
        return None

    issue = data.get('issue', {})
    repo = data.get('repository', {})
    repo_name = repo.get('full_name', '알 수 없음')
    issue_number = issue.get('number', '?')
    title = issue.get('title', '제목 없음')
    user = issue.get('user', {}).get('login', '알 수 없음')
    html_url = issue.get('html_url', '')

    action_emoji = {
        'opened': '🟢',
        'closed': '🔴',
        'reopened': '🔄'
    }.get(action, '')

    parsed_message = (
        f"{action_emoji} *Issue #{issue_number}*\n"
        f"*{repo_name}*\n"
        f"{title}\n"
        f"by {user}\n"
        f"[이슈 보기]({html_url})"
    )

    return parsed_message


def parse_issue_comment_event(data):
    """
    Issue 댓글 이벤트 메시지 생성
    
    표시 정보:
    - 이슈 번호
    - 레포지토리 이름
    - 이슈 제목
    - 댓글 작성자
    """
    issue = data.get('issue', {})
    comment = data.get('comment', {})
    repo = data.get('repository', {})
    
    repo_name = repo.get('full_name', '알 수 없음')
    issue_number = issue.get('number', '?')
    title = issue.get('title', '제목 없음')
    user = comment.get('user', {}).get('login', '알 수 없음')
    html_url = comment.get('html_url', '')

    parsed_message = (
        f"💬 *Comment on #{issue_number}*\n"
        f"*{repo_name}*\n"
        f"{title}\n"
        f"by {user}\n"
        f"[댓글 보기]({html_url})"
    )

    return parsed_message


def parse_ping_event(data):
    """
    ping 이벤트(웹훅 등록시 테스트)용 간단 응답
    """
    zen = data.get('zen', '')
    hook_id = data.get('hook_id', '')
    parsed_message = (
        f" [Ping 이벤트] \n"
        f"메시지: {zen}\n"
        f"Hook ID: {hook_id}"
    )
    return parsed_message


def parse_other_event(event_type, data):
    """
    그 외 이벤트 타입에 대한 처리
    """
    # 어떤 정보들이 들어오는지는 event_type별로 GitHub Docs 참고 가능
    repository = data.get('repository', {})
    repo_name = repository.get('full_name', '알 수 없음')

    parsed_message = (
        f" [기타 이벤트: {event_type}] \n"
        f"레포지토리: {repo_name}\n"
        f"데이터 전체:\n{data}"
    )
    return parsed_message


app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    # GitHub에서 보내는 이벤트 타입
    event_type = request.headers.get('X-GitHub-Event', 'unknown')
    data = request.json  # GitHub에서 보낸 데이터 (dict 형태)

    # 이벤트 타입별로 분기 처리
    if event_type == 'ping':
        message = parse_ping_event(data)
    elif event_type == 'push':
        message = parse_push_event(data)
    elif event_type == 'pull_request':
        message = parse_pull_request_event(data)
    elif event_type == 'issues':
        message = parse_issues_event(data)
    elif event_type == 'issue_comment':
        message = parse_issue_comment_event(data)
    else:
        # 아직 별도 처리가 없는 이벤트들은 기본(기타) 처리
        message = parse_other_event(event_type, data)

    # Telegram 메시지 보내기
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    # 디버그용
    print("===== Payload to Telegram =====")
    print(payload)
    print("===============================")

    # 실제 텔레그램 전송
    requests.post(telegram_url, json=payload)

    return jsonify({"status": "success"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
