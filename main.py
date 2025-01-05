from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import os

# .env 파일에서 환경변수 로드
load_dotenv()

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # 수신할 채팅방 ID (봇과 대화 후 @get_id_bot 사용 가능)
TELEGRAM_WORK_CHAT_ID = os.getenv("TELEGRAM_WORK_CHAT_ID")

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("환경변수 TELEGRAM_BOT_TOKEN과 TELEGRAM_CHAT_ID가 설정되어 있지 않습니다.")


def parse_push_event(data):
    """
    Push 이벤트 메시지 생성
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
        remaining = len(commits) - 1
        remaining_info = f"\n추가 커밋 {remaining}개" if remaining > 0 else ""
    else:
        commit_message = "커밋 없음"
        commit_url = ""
        remaining_info = ""

    parsed_message = (
        f"📦 *{commit_message}*\n"
        f"레포 : {repo_name}\n"
        f"작성자 : {pusher_name}\n"
        f"링크 : [커밋 보기]({commit_url}){remaining_info}"
    )

    return parsed_message


def parse_pull_request_event(data):
    """
    Pull Request 이벤트 메시지 생성
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
        'opened': '💫',
        'closed': '🔒',
        'reopened': '🔄'
    }.get(action, '')

    parsed_message = (
        f"{action_emoji} *{title}*\n"
        f"레포 : {repo_name}\n"
        f"작성자 : {user}\n"
        f"링크 : [PR #{pr_number}]({html_url})"
    )

    return parsed_message


def parse_issues_event(data):
    """
    Issue 이벤트 메시지 생성
    
    지원하는 액션:
    - opened: 이슈 생성 (🟢)
    - closed: 이슈 닫힘 (🔴)
    - reopened: 이슈 재오픈 (🔄)
    - deleted: 이슈 삭제 (🗑️)
    
    Args:
        data (dict): GitHub webhook 이벤트 데이터
        
    Returns:
        str: 포맷팅된 메시지
    """
    action = data.get('action', '')
    issue = data.get('issue', {})
    
    if action not in ['opened', 'closed', 'reopened', 'deleted']:
        return None
        
    repo = data.get('repository', {})
    repo_name = repo.get('full_name', '알 수 없음')
    title = issue.get('title', '제목 없음')
    user = issue.get('user', {}).get('login', '알 수 없음')
    html_url = issue.get('html_url', '')

    action_emoji = {
        'opened': '🟢',
        'closed': '🔴',
        'reopened': '🔄',
        'deleted': '🗑️'
    }.get(action, '')

    parsed_message = (
        f"{action_emoji} *{title}*\n"
        f"레포 : {repo_name}\n"
        f"작성자 : {user}\n"
        f"링크 : [이슈 보기]({html_url})"
    )

    return parsed_message


def parse_issue_comment_event(data):
    """
    Issue 댓글 이벤트 메시지 생성
    
    Args:
        data (dict): GitHub webhook 이벤트 데이터
        
    Returns:
        str: 포맷팅된 메시지
    """
    comment = data.get('comment', {})
    issue = data.get('issue', {})
    repo = data.get('repository', {})
    
    repo_name = repo.get('full_name', '알 수 없음')
    issue_title = issue.get('title', '제목 없음')
    user = comment.get('user', {}).get('login', '알 수 없음')
    html_url = comment.get('html_url', '')

    parsed_message = (
        f"🗣️ *{issue_title}*\n"
        f"레포 : {repo_name}\n"
        f"작성자 : {user}\n"
        f"링크 : [댓글 보기]({html_url})"
    )

    return parsed_message


def parse_ping_event(data):
    """
    Ping 이벤트 메시지 생성 (웹훅 등록 테스트용)
    
    Args:
        data (dict): GitHub webhook 이벤트 데이터
        
    Returns:
        str: 포맷팅된 메시지
    """
    zen = data.get('zen', '')
    hook_id = data.get('hook_id', '')
    parsed_message = (
        f" [Ping 이벤트] \n"
        f"메시지: {zen}\n"
        f"Hook ID: {hook_id}"
    )
    return parsed_message


def parse_pull_request_review_event(data):
    """
    Pull Request Review 이벤트 메시지 생성
    
    지원하는 액션:
    - submitted: 리뷰 제출 
      - commented (💭): 일반 코멘트
      - approved (✅): 승인
      - changes_requested (❌): 변경 요청
    - dismissed: 리뷰 철회 (🔄)
    
    Args:
        data (dict): GitHub webhook 이벤트 데이터
        
    Returns:
        str: 포맷팅된 메시지
    """
    action = data.get('action', '')
    review = data.get('review', {})
    pull_request = data.get('pull_request', {})
    
    if action not in ['submitted', 'dismissed']:
        return None
        
    repo = data.get('repository', {})
    repo_name = repo.get('full_name', '알 수 없음')
    pr_title = pull_request.get('title', '제목 없음')
    reviewer = review.get('user', {}).get('login', '알 수 없음')
    review_url = review.get('html_url', '')
    
    # 리뷰 상태에 따른 이모지 결정
    state = review.get('state', '')
    if action == 'submitted':
        action_emoji = {
            'commented': '💭',
            'approved': '✅',
            'changes_requested': '❌'
        }.get(state, '💭')
    else:  # dismissed
        action_emoji = '🔄'
    
    # 리뷰 내용
    review_body = review.get('body', '').strip()
    review_comment = f"\n코멘트 : {review_body}" if review_body else ""
    
    parsed_message = (
        f"{action_emoji} *{pr_title}*\n"
        f"레포 : {repo_name}\n"
        f"리뷰어 : {reviewer}{review_comment}\n"
        f"링크 : [리뷰 보기]({review_url})"
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


def send_telegram_message(message, is_issue=False):
    """
    텔레그램으로 메시지를 전송하는 함수
    
    Args:
        message (str): 전송할 메시지
        is_issue (bool): Issue 관련 메시지인지 여부
    """
    chat_id = TELEGRAM_CHAT_ID if is_issue else TELEGRAM_WORK_CHAT_ID
    if not chat_id:
        return
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=data)


app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    """
    GitHub webhook 엔드포인트
    
    지원하는 이벤트:
    - ping: 웹훅 등록 테스트
    - push: 코드 푸시
    - pull_request: PR 생성/수정/닫힘
    - pull_request_review: PR 리뷰
    - issues: 이슈 생성/수정/닫힘
    - issue_comment: 이슈 댓글
    """
    event_type = request.headers.get("X-GitHub-Event")
    data = request.json

    if event_type == "ping":
        message = parse_ping_event(data)
        if message:
            send_telegram_message(message)
    elif event_type == "push":
        message = parse_push_event(data)
        if message:
            send_telegram_message(message)
    elif event_type == "pull_request":
        message = parse_pull_request_event(data)
        if message:
            send_telegram_message(message)
    elif event_type == "pull_request_review":
        message = parse_pull_request_review_event(data)
        if message:
            send_telegram_message(message)
    elif event_type == "issues":
        message = parse_issues_event(data)
        if message:
            send_telegram_message(message, is_issue=True)
    elif event_type == "issue_comment":
        message = parse_issue_comment_event(data)
        if message:
            send_telegram_message(message, is_issue=True)
    else:
        message = parse_other_event(event_type, data)
        if message:
            send_telegram_message(message)

    return jsonify({"status": "success"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
