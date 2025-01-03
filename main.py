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
    push 이벤트에 대한 메시지 파싱
    """
    repository = data.get('repository', {})
    pusher = data.get('pusher', {})
    commits = data.get('commits', [])

    repo_name = repository.get('full_name', '알 수 없음')
    pusher_name = pusher.get('name', '알 수 없음')

    commit_messages = []
    for commit in commits:
        message = commit.get('message', '')
        commit_url = commit.get('url', '')
        commit_messages.append(f"- {message} ({commit_url})")

    commit_str = "\n".join(commit_messages) if commit_messages else "커밋이 없습니다."

    parsed_message = (
        f" [Push 이벤트] \n"
        f"레포지토리: {repo_name}\n"
        f"푸시한 사람: {pusher_name}\n"
        f"커밋 내용:\n{commit_str}"
    )

    return parsed_message


def parse_pull_request_event(data):
    """
    pull_request 이벤트에 대한 메시지 파싱
    """
    action = data.get('action', '')
    pr = data.get('pull_request', {})
    repository = data.get('repository', {})

    repo_name = repository.get('full_name', '알 수 없음')
    pr_title = pr.get('title', '')
    pr_number = pr.get('number', '')
    pr_user = pr.get('user', {}).get('login', '알 수 없음')
    pr_url = pr.get('html_url', '')

    parsed_message = (
        f" [Pull Request 이벤트] \n"
        f"레포지토리: {repo_name}\n"
        f"액션: {action}\n"
        f"PR 번호: #{pr_number}\n"
        f"제목: {pr_title}\n"
        f"작성자: {pr_user}\n"
        f"URL: {pr_url}"
    )
    return parsed_message


def parse_issues_event(data):
    """
    issues 이벤트에 대한 메시지 파싱
    지원하는 액션:
    - opened, closed, reopened: 이슈 열기/닫기/재열기
    - assigned, unassigned: 이슈 할당/할당해제
    - labeled, unlabeled: 라벨 추가/제거
    - milestoned, demilestoned: 마일스톤 추가/제거
    - locked, unlocked: 이슈 잠금/잠금해제
    """
    action = data.get('action', '')
    issue = data.get('issue', {})
    repository = data.get('repository', {})

    repo_name = repository.get('full_name', '알 수 없음')
    issue_title = issue.get('title', '')
    issue_number = issue.get('number', '')
    issue_user = issue.get('user', {}).get('login', '알 수 없음')
    issue_url = issue.get('html_url', '')

    # 기본 메시지 구성
    parsed_message = (
        f" [Issues 이벤트] \n"
        f"레포지토리: {repo_name}\n"
        f"액션: {action}\n"
        f"이슈 번호: #{issue_number}\n"
        f"제목: {issue_title}\n"
        f"작성자: {issue_user}\n"
        f"URL: {issue_url}"
    )

    # 액션별 추가 정보
    if action in ['assigned', 'unassigned']:
        assignee = data.get('assignee', {}).get('login', '알 수 없음')
        parsed_message += f"\n담당자: {assignee}"
    
    elif action in ['labeled', 'unlabeled']:
        label = data.get('label', {}).get('name', '알 수 없음')
        parsed_message += f"\n라벨: {label}"
    
    elif action in ['milestoned', 'demilestoned']:
        milestone = issue.get('milestone', {}).get('title', '알 수 없음')
        parsed_message += f"\n마일스톤: {milestone}"
    
    elif action in ['locked', 'unlocked']:
        lock_reason = issue.get('active_lock_reason', '이유 없음')
        if action == 'locked':
            parsed_message += f"\n잠금 이유: {lock_reason}"

    return parsed_message


def parse_issue_comment_event(data):
    """
    issue_comment 이벤트에 대한 메시지 파싱
    """
    action = data.get('action', '')
    comment = data.get('comment', {})
    issue = data.get('issue', {})
    repository = data.get('repository', {})

    repo_name = repository.get('full_name', '알 수 없음')
    issue_number = issue.get('number', '')
    comment_user = comment.get('user', {}).get('login', '알 수 없음')
    comment_body = comment.get('body', '')
    comment_url = comment.get('html_url', '')

    parsed_message = (
        f" [Issue Comment 이벤트] \n"
        f"레포지토리: {repo_name}\n"
        f"액션: {action}\n"
        f"이슈 번호: #{issue_number}\n"
        f"댓글 작성자: {comment_user}\n"
        f"내용: {comment_body}\n"
        f"URL: {comment_url}"
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
