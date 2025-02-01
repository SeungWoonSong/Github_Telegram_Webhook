from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import os
import json

# .env 파일 로드
load_dotenv()

# Telegram 설정
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_DEFAULT_CHAT_ID = os.getenv("TELEGRAM_DEFAULT_CHAT_ID")

# 이벤트별 채팅방 매핑 로드
EVENT_CHAT_MAPPING = {}
event_mapping_str = os.getenv("EVENT_CHAT_MAPPING", "{}")
try:
    raw_mapping = json.loads(event_mapping_str)
    # "event1,event2": "chat_id" 형식의 매핑을 개별 이벤트로 분리
    for events, chat_id in raw_mapping.items():
        for event in events.split(","):
            EVENT_CHAT_MAPPING[event.strip()] = chat_id
except json.JSONDecodeError:
    print("Warning: Invalid EVENT_CHAT_MAPPING format in .env file")

def get_chat_id_for_event(event_type):
    """
    주어진 이벤트 타입에 대한 채팅방 ID를 반환합니다.
    매핑에 없는 경우 기본 채팅방 ID를 반환합니다.
    """
    return EVENT_CHAT_MAPPING.get(event_type, TELEGRAM_DEFAULT_CHAT_ID)

def send_telegram_message(message, event_type):
    """
    텔레그램으로 메시지를 전송합니다.
    이벤트 타입에 따라 적절한 채팅방으로 전송됩니다.
    """
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not set")
        return
    
    chat_id = get_chat_id_for_event(event_type)
    if not chat_id:
        print(f"Error: No chat ID configured for event type: {event_type}")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to Telegram: {e}")


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
        f"🗣️ *{issue_title}의 댓글*\n"
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


def parse_discussion_event(data):
    """
    Discussion 이벤트 메시지 생성
    
    지원하는 액션:
    - created: 토론 생성 (💬)
    - edited: 토론 수정 (📝)
    - deleted: 토론 삭제 (🗑️)
    - pinned: 토론 고정 (📌)
    - unpinned: 토론 고정 해제 (📍)
    - locked: 토론 잠금 (🔒)
    - unlocked: 토론 잠금 해제 (🔓)
    - transferred: 토론 이전 (↗️)
    
    Args:
        data (dict): GitHub webhook 이벤트 데이터
        
    Returns:
        str: 포맷팅된 메시지
    """
    action = data.get('action', '')
    discussion = data.get('discussion', {})
    
    if action not in ['created', 'edited', 'deleted', 'pinned', 'unpinned', 'locked', 'unlocked', 'transferred']:
        return None
        
    repo = data.get('repository', {})
    repo_name = repo.get('full_name', '알 수 없음')
    title = discussion.get('title', '제목 없음')
    user = discussion.get('user', {}).get('login', '알 수 없음')
    html_url = discussion.get('html_url', '')

    action_emoji = {
        'created': '💬',
        'edited': '📝',
        'deleted': '🗑️',
        'pinned': '📌',
        'unpinned': '📍',
        'locked': '🔒',
        'unlocked': '🔓',
        'transferred': '↗️'
    }.get(action, '')

    parsed_message = (
        f"{action_emoji} *{title}*\n"
        f"레포 : {repo_name}\n"
        f"작성자 : {user}\n"
        f"링크 : [토론 보기]({html_url})"
    )

    return parsed_message


def parse_discussion_comment_event(data):
    """
    Discussion 댓글 이벤트 메시지 생성
    
    지원하는 액션:
    - created: 댓글 생성
    - edited: 댓글 수정
    - deleted: 댓글 삭제
    
    Args:
        data (dict): GitHub webhook 이벤트 데이터
        
    Returns:
        str: 포맷팅된 메시지
    """
    action = data.get('action', '')
    comment = data.get('comment', {})
    discussion = data.get('discussion', {})
    
    if action not in ['created', 'edited', 'deleted']:
        return None
        
    repo = data.get('repository', {})
    repo_name = repo.get('full_name', '알 수 없음')
    discussion_title = discussion.get('title', '제목 없음')
    user = comment.get('user', {}).get('login', '알 수 없음')
    html_url = comment.get('html_url', '')

    action_emoji = {
        'created': '💭',
        'edited': '✏️',
        'deleted': '🗑️'
    }.get(action, '')

    parsed_message = (
        f"{action_emoji} *{discussion_title}의 댓글*\n"
        f"레포 : {repo_name}\n"
        f"작성자 : {user}\n"
        f"링크 : [댓글 보기]({html_url})"
    )

    return parsed_message


def parse_branch_protection_rule_event(data):
    """
    Branch Protection Rule 이벤트 메시지 생성
    
    지원하는 액션:
    - created: 규칙 생성
    - edited: 규칙 수정
    - deleted: 규칙 삭제
    
    Args:
        data (dict): GitHub webhook 이벤트 데이터
        
    Returns:
        str: 포맷팅된 메시지
    """
    action = data.get('action', '')
    rule = data.get('rule', {})
    
    if action not in ['created', 'edited', 'deleted']:
        return None
        
    repo = data.get('repository', {})
    repo_name = repo.get('full_name', '알 수 없음')
    pattern = rule.get('pattern', '알 수 없음')

    action_emoji = {
        'created': '🛡️',
        'edited': '🔧',
        'deleted': '🗑️'
    }.get(action, '')

    parsed_message = (
        f"{action_emoji} *브랜치 보호 규칙 {action}*\n"
        f"레포 : {repo_name}\n"
        f"패턴 : {pattern}"
    )

    return parsed_message


def parse_check_run_event(data):
    """
    Check Run 이벤트 메시지 생성
    
    지원하는 액션:
    - completed: 체크 완료
    
    Args:
        data (dict): GitHub webhook 이벤트 데이터
        
    Returns:
        str: 포맷팅된 메시지
    """
    action = data.get('action', '')
    check_run = data.get('check_run', {})
    
    if action != 'completed':
        return None
        
    repo = data.get('repository', {})
    repo_name = repo.get('full_name', '알 수 없음')
    name = check_run.get('name', '알 수 없음')
    conclusion = check_run.get('conclusion', '알 수 없음')
    html_url = check_run.get('html_url', '')

    conclusion_emoji = {
        'success': '✅',
        'failure': '❌',
        'neutral': '➖',
        'cancelled': '🚫',
        'skipped': '⏭️',
        'timed_out': '⏰',
        'action_required': '⚠️'
    }.get(conclusion, '❓')

    parsed_message = (
        f"{conclusion_emoji} *{name}*\n"
        f"레포 : {repo_name}\n"
        f"결과 : {conclusion}\n"
        f"링크 : [상세 보기]({html_url})"
    )

    return parsed_message


def parse_code_scanning_alert_event(data):
    """
    Code Scanning Alert 이벤트 메시지 생성
    
    지원하는 액션:
    - created: 알림 생성
    - reopened: 알림 재오픈
    - closed: 알림 닫힘
    - fixed: 알림 해결
    
    Args:
        data (dict): GitHub webhook 이벤트 데이터
        
    Returns:
        str: 포맷팅된 메시지
    """
    action = data.get('action', '')
    alert = data.get('alert', {})
    
    if action not in ['created', 'reopened', 'closed', 'fixed']:
        return None
        
    repo = data.get('repository', {})
    repo_name = repo.get('full_name', '알 수 없음')
    rule = alert.get('rule', {})
    rule_desc = rule.get('description', '알 수 없음')
    html_url = alert.get('html_url', '')
    severity = alert.get('severity', '알 수 없음')

    action_emoji = {
        'created': '🔍',
        'reopened': '🔄',
        'closed': '🔒',
        'fixed': '✅'
    }.get(action, '')

    severity_emoji = {
        'critical': '⚠️',
        'high': '🔴',
        'medium': '🟡',
        'low': '🟢',
        'warning': '💡',
        'note': 'ℹ️'
    }.get(severity.lower(), '❓')

    parsed_message = (
        f"{action_emoji} *코드 스캔 알림 {action}*\n"
        f"{severity_emoji} 심각도: {severity}\n"
        f"레포 : {repo_name}\n"
        f"설명 : {rule_desc}\n"
        f"링크 : [알림 보기]({html_url})"
    )

    return parsed_message


def parse_dependabot_alert_event(data):
    """
    Dependabot Alert 이벤트 메시지 생성
    
    지원하는 액션:
    - created: 알림 생성
    - dismissed: 알림 무시
    - fixed: 알림 해결
    - reintroduced: 알림 재발생
    
    Args:
        data (dict): GitHub webhook 이벤트 데이터
        
    Returns:
        str: 포맷팅된 메시지
    """
    action = data.get('action', '')
    alert = data.get('alert', {})
    
    if action not in ['created', 'dismissed', 'fixed', 'reintroduced']:
        return None
        
    repo = data.get('repository', {})
    repo_name = repo.get('full_name', '알 수 없음')
    package_name = alert.get('dependency', {}).get('package', {}).get('name', '알 수 없음')
    severity = alert.get('security_advisory', {}).get('severity', '알 수 없음')
    html_url = alert.get('html_url', '')

    action_emoji = {
        'created': '🔍',
        'dismissed': '🚫',
        'fixed': '✅',
        'reintroduced': '↩️'
    }.get(action, '')

    severity_emoji = {
        'critical': '⚠️',
        'high': '🔴',
        'medium': '🟡',
        'low': '🟢'
    }.get(severity.lower(), '❓')

    parsed_message = (
        f"{action_emoji} *Dependabot 알림 {action}*\n"
        f"{severity_emoji} 심각도: {severity}\n"
        f"레포 : {repo_name}\n"
        f"패키지 : {package_name}\n"
        f"링크 : [알림 보기]({html_url})"
    )

    return parsed_message


def parse_commit_comment_event(data):
    """
    Commit Comment 이벤트 메시지 생성
    
    지원하는 액션:
    - created: 댓글 생성
    
    Args:
        data (dict): GitHub webhook 이벤트 데이터
        
    Returns:
        str: 포맷팅된 메시지
    """
    comment = data.get('comment', {})
    repo = data.get('repository', {})
    
    repo_name = repo.get('full_name', '알 수 없음')
    commit_id = comment.get('commit_id', '')[:7]  # Short SHA
    user = comment.get('user', {}).get('login', '알 수 없음')
    html_url = comment.get('html_url', '')

    parsed_message = (
        f"💬 *커밋 {commit_id}에 댓글이 추가됨*\n"
        f"레포 : {repo_name}\n"
        f"작성자 : {user}\n"
        f"링크 : [댓글 보기]({html_url})"
    )

    return parsed_message


def parse_create_delete_event(data, event_type):
    """
    Create/Delete 이벤트 메시지 생성
    
    Args:
        data (dict): GitHub webhook 이벤트 데이터
        event_type (str): 'create' 또는 'delete'
        
    Returns:
        str: 포맷팅된 메시지
    """
    ref_type = data.get('ref_type', '')  # branch or tag
    ref = data.get('ref', '')  # The name of the branch or tag
    repo = data.get('repository', {})
    repo_name = repo.get('full_name', '알 수 없음')

    emoji = '🌱' if event_type == 'create' else '🗑️'
    action = '생성됨' if event_type == 'create' else '삭제됨'
    ref_type_kr = '브랜치' if ref_type == 'branch' else '태그'

    parsed_message = (
        f"{emoji} *{ref_type_kr} {action}*\n"
        f"레포 : {repo_name}\n"
        f"이름 : {ref}"
    )

    return parsed_message


def parse_deployment_event(data):
    """
    Deployment 이벤트 메시지 생성
    
    Args:
        data (dict): GitHub webhook 이벤트 데이터
        
    Returns:
        str: 포맷팅된 메시지
    """
    deployment = data.get('deployment', {})
    repo = data.get('repository', {})
    
    repo_name = repo.get('full_name', '알 수 없음')
    environment = deployment.get('environment', '알 수 없음')
    creator = deployment.get('creator', {}).get('login', '알 수 없음')
    ref = deployment.get('ref', '알 수 없음')

    parsed_message = (
        f"🚀 *새로운 배포*\n"
        f"레포 : {repo_name}\n"
        f"환경 : {environment}\n"
        f"브랜치 : {ref}\n"
        f"작성자 : {creator}"
    )

    return parsed_message


def parse_deployment_status_event(data):
    """
    Deployment Status 이벤트 메시지 생성
    
    Args:
        data (dict): GitHub webhook 이벤트 데이터
        
    Returns:
        str: 포맷팅된 메시지
    """
    deployment_status = data.get('deployment_status', {})
    deployment = data.get('deployment', {})
    repo = data.get('repository', {})
    
    repo_name = repo.get('full_name', '알 수 없음')
    environment = deployment.get('environment', '알 수 없음')
    state = deployment_status.get('state', '알 수 없음')
    creator = deployment_status.get('creator', {}).get('login', '알 수 없음')

    state_emoji = {
        'success': '✅',
        'failure': '❌',
        'error': '⚠️',
        'inactive': '💤',
        'in_progress': '🔄',
        'queued': '⏳',
        'pending': '⏳'
    }.get(state, '❓')

    parsed_message = (
        f"{state_emoji} *배포 상태 업데이트*\n"
        f"레포 : {repo_name}\n"
        f"환경 : {environment}\n"
        f"상태 : {state}\n"
        f"작성자 : {creator}"
    )

    return parsed_message


def parse_fork_event(data):
    """
    Fork 이벤트 메시지 생성
    
    Args:
        data (dict): GitHub webhook 이벤트 데이터
        
    Returns:
        str: 포맷팅된 메시지
    """
    forkee = data.get('forkee', {})
    repo = data.get('repository', {})
    
    repo_name = repo.get('full_name', '알 수 없음')
    fork_name = forkee.get('full_name', '알 수 없음')
    fork_url = forkee.get('html_url', '')

    parsed_message = (
        f"🍴 *저장소가 포크됨*\n"
        f"원본 : {repo_name}\n"
        f"포크 : {fork_name}\n"
        f"링크 : [포크 보기]({fork_url})"
    )

    return parsed_message


def parse_repository_event(data):
    """
    Repository 이벤트 메시지 생성
    
    지원하는 액션:
    - created: 저장소 생성
    - deleted: 저장소 삭제
    - archived: 저장소 보관
    - unarchived: 저장소 보관 해제
    - publicized: 저장소 공개
    - privatized: 저장소 비공개
    
    Args:
        data (dict): GitHub webhook 이벤트 데이터
        
    Returns:
        str: 포맷팅된 메시지
    """
    action = data.get('action', '')
    repo = data.get('repository', {})
    
    if action not in ['created', 'deleted', 'archived', 'unarchived', 'publicized', 'privatized']:
        return None
        
    repo_name = repo.get('full_name', '알 수 없음')
    html_url = repo.get('html_url', '')

    action_emoji = {
        'created': '📁',
        'deleted': '🗑️',
        'archived': '📦',
        'unarchived': '📤',
        'publicized': '🌍',
        'privatized': '🔒'
    }.get(action, '')

    parsed_message = (
        f"{action_emoji} *저장소 {action}*\n"
        f"레포 : {repo_name}\n"
        f"링크 : [저장소 보기]({html_url})"
    )

    return parsed_message


def parse_gollum_event(data):
    """
    Wiki (Gollum) 이벤트 메시지 생성
    
    Args:
        data (dict): GitHub webhook 이벤트 데이터
        
    Returns:
        str: 포맷팅된 메시지
    """
    pages = data.get('pages', [])
    repo = data.get('repository', {})
    
    if not pages:
        return None
        
    repo_name = repo.get('full_name', '알 수 없음')
    
    # 첫 번째 페이지 정보만 표시
    page = pages[0]
    page_name = page.get('title', '알 수 없음')
    action = page.get('action', '알 수 없음')
    html_url = page.get('html_url', '')
    
    remaining = len(pages) - 1
    remaining_info = f"\n추가 페이지 {remaining}개" if remaining > 0 else ""

    action_emoji = {
        'created': '📝',
        'edited': '✏️',
        'deleted': '🗑️'
    }.get(action, '📚')

    parsed_message = (
        f"{action_emoji} *Wiki 페이지 {action}*\n"
        f"레포 : {repo_name}\n"
        f"페이지 : {page_name}\n"
        f"링크 : [Wiki 보기]({html_url}){remaining_info}"
    )

    return parsed_message


def parse_pull_request_review_comment_event(data):
    """
    Pull Request Review Comment 이벤트 메시지 생성
    
    지원하는 액션:
    - created: 댓글 생성
    - edited: 댓글 수정
    - deleted: 댓글 삭제
    
    Args:
        data (dict): GitHub webhook 이벤트 데이터
        
    Returns:
        str: 포맷팅된 메시지
    """
    action = data.get('action', '')
    comment = data.get('comment', {})
    pull_request = data.get('pull_request', {})
    
    if action not in ['created', 'edited', 'deleted']:
        return None
        
    repo = data.get('repository', {})
    repo_name = repo.get('full_name', '알 수 없음')
    pr_title = pull_request.get('title', '제목 없음')
    user = comment.get('user', {}).get('login', '알 수 없음')
    html_url = comment.get('html_url', '')

    action_emoji = {
        'created': '💭',
        'edited': '✏️',
        'deleted': '🗑️'
    }.get(action, '')

    parsed_message = (
        f"{action_emoji} *PR 리뷰 댓글 {action}*\n"
        f"PR : {pr_title}\n"
        f"레포 : {repo_name}\n"
        f"작성자 : {user}\n"
        f"링크 : [댓글 보기]({html_url})"
    )

    return parsed_message


def parse_branch_protection_configuration_event(data):
    """
    Branch Protection Configuration 이벤트 메시지 생성
    
    지원하는 액션:
    - edited: 설정 변경
    
    Args:
        data (dict): GitHub webhook 이벤트 데이터
        
    Returns:
        str: 포맷팅된 메시지
    """
    changes = data.get('changes', {})
    repo = data.get('repository', {})
    
    repo_name = repo.get('full_name', '알 수 없음')
    protected_branch = data.get('branch', '알 수 없음')

    parsed_message = (
        f"🔧 *브랜치 보호 설정 변경*\n"
        f"레포 : {repo_name}\n"
        f"브랜치 : {protected_branch}"
    )

    return parsed_message


def parse_check_suite_event(data):
    """
    Check Suite 이벤트 메시지 생성
    
    지원하는 액션:
    - completed: 체크 스위트 완료
    
    Args:
        data (dict): GitHub webhook 이벤트 데이터
        
    Returns:
        str: 포맷팅된 메시지
    """
    action = data.get('action', '')
    check_suite = data.get('check_suite', {})
    
    if action != 'completed':
        return None
        
    repo = data.get('repository', {})
    repo_name = repo.get('full_name', '알 수 없음')
    conclusion = check_suite.get('conclusion', '알 수 없음')
    html_url = check_suite.get('html_url', '')

    conclusion_emoji = {
        'success': '✅',
        'failure': '❌',
        'neutral': '➖',
        'cancelled': '🚫',
        'skipped': '⏭️',
        'timed_out': '⏰',
        'action_required': '⚠️'
    }.get(conclusion, '❓')

    parsed_message = (
        f"{conclusion_emoji} *체크 스위트 완료*\n"
        f"레포 : {repo_name}\n"
        f"결과 : {conclusion}\n"
        f"링크 : [상세 보기]({html_url})"
    )

    return parsed_message


def parse_deployment_protection_rule_event(data):
    """
    Deployment Protection Rule 이벤트 메시지 생성
    
    지원하는 액션:
    - requested: 배포 보호 규칙 검사 요청
    
    Args:
        data (dict): GitHub webhook 이벤트 데이터
        
    Returns:
        str: 포맷팅된 메시지
    """
    environment = data.get('environment', {})
    deployment = data.get('deployment', {})
    repo = data.get('repository', {})
    
    repo_name = repo.get('full_name', '알 수 없음')
    env_name = environment.get('name', '알 수 없음')
    ref = deployment.get('ref', '알 수 없음')

    parsed_message = (
        f"🛡️ *배포 보호 규칙 검사 요청*\n"
        f"레포 : {repo_name}\n"
        f"환경 : {env_name}\n"
        f"브랜치 : {ref}"
    )

    return parsed_message


def parse_deployment_review_event(data):
    """
    Deployment Review 이벤트 메시지 생성
    
    지원하는 액션:
    - approved: 배포 승인
    - rejected: 배포 거절
    
    Args:
        data (dict): GitHub webhook 이벤트 데이터
        
    Returns:
        str: 포맷팅된 메시지
    """
    action = data.get('action', '')
    deployment = data.get('deployment', {})
    
    if action not in ['approved', 'rejected']:
        return None
        
    repo = data.get('repository', {})
    repo_name = repo.get('full_name', '알 수 없음')
    environment = deployment.get('environment', '알 수 없음')
    reviewer = data.get('reviewer', {}).get('login', '알 수 없음')

    action_emoji = {
        'approved': '✅',
        'rejected': '❌'
    }.get(action, '')

    action_kr = '승인됨' if action == 'approved' else '거절됨'

    parsed_message = (
        f"{action_emoji} *배포 {action_kr}*\n"
        f"레포 : {repo_name}\n"
        f"환경 : {environment}\n"
        f"검토자 : {reviewer}"
    )

    return parsed_message


def parse_public_event(data):
    """
    Public 이벤트 메시지 생성
    
    Args:
        data (dict): GitHub webhook 이벤트 데이터
        
    Returns:
        str: 포맷팅된 메시지
    """
    repo = data.get('repository', {})
    
    repo_name = repo.get('full_name', '알 수 없음')
    html_url = repo.get('html_url', '')

    parsed_message = (
        f"🌍 *저장소가 공개로 전환됨*\n"
        f"레포 : {repo_name}\n"
        f"링크 : [저장소 보기]({html_url})"
    )

    return parsed_message


def parse_github_app_event(data, event_type):
    """
    GitHub App 관련 이벤트 메시지 생성
    
    Args:
        data (dict): GitHub webhook 이벤트 데이터
        event_type (str): 이벤트 타입 (authorization, installation, installation_repositories)
        
    Returns:
        str: 포맷팅된 메시지
    """
    if event_type == 'github_app_authorization':
        action = 'revoked'  # 항상 revoked
        app = data.get('app', {})
        app_name = app.get('name', '알 수 없음')
        
        parsed_message = (
            f"🔒 *GitHub 앱 인증 해제*\n"
            f"앱 : {app_name}"
        )
    
    elif event_type == 'installation':
        action = data.get('action', '')
        installation = data.get('installation', {})
        app = installation.get('app', {})
        
        if action not in ['created', 'deleted', 'suspend', 'unsuspend']:
            return None
            
        app_name = app.get('name', '알 수 없음')
        account = data.get('sender', {}).get('login', '알 수 없음')
        
        action_emoji = {
            'created': '📥',
            'deleted': '🗑️',
            'suspend': '⏸️',
            'unsuspend': '▶️'
        }.get(action, '')
        
        action_kr = {
            'created': '설치됨',
            'deleted': '제거됨',
            'suspend': '일시중지됨',
            'unsuspend': '재개됨'
        }.get(action, action)
        
        parsed_message = (
            f"{action_emoji} *GitHub 앱 {action_kr}*\n"
            f"앱 : {app_name}\n"
            f"계정 : {account}"
        )
    
    elif event_type == 'installation_repositories':
        action = data.get('action', '')
        installation = data.get('installation', {})
        app = installation.get('app', {})
        
        if action not in ['added', 'removed']:
            return None
            
        app_name = app.get('name', '알 수 없음')
        repos_added = data.get('repositories_added', [])
        repos_removed = data.get('repositories_removed', [])
        
        repos = repos_added if action == 'added' else repos_removed
        repo_names = [repo.get('full_name', '') for repo in repos]
        
        action_emoji = '📥' if action == 'added' else '📤'
        action_kr = '추가됨' if action == 'added' else '제거됨'
        
        parsed_message = (
            f"{action_emoji} *GitHub 앱 저장소 {action_kr}*\n"
            f"앱 : {app_name}\n"
            f"저장소:\n" + '\n'.join(f"- {name}" for name in repo_names)
        )
    
    else:
        return None

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


def send_telegram_message(message, event_type):
    """
    텔레그램으로 메시지를 전송합니다.
    이벤트 타입에 따라 적절한 채팅방으로 전송됩니다.
    """
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not set")
        return
    
    chat_id = get_chat_id_for_event(event_type)
    if not chat_id:
        print(f"Error: No chat ID configured for event type: {event_type}")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to Telegram: {e}")


app = Flask(__name__)

# 이벤트 타입별 파서 매핑
EVENT_PARSERS = {
    # 기본 이벤트
    "ping": parse_ping_event,
    "push": parse_push_event,
    
    # 브랜치 관련
    "branch_protection_configuration": parse_branch_protection_configuration_event,
    "branch_protection_rule": parse_branch_protection_rule_event,
    
    # CI/CD 및 체크
    "check_run": parse_check_run_event,
    "check_suite": parse_check_suite_event,
    
    # 코드 품질 및 보안
    "code_scanning_alert": parse_code_scanning_alert_event,
    "dependabot_alert": parse_dependabot_alert_event,
    
    # 커밋 및 변경사항
    "commit_comment": parse_commit_comment_event,
    "create": lambda data: parse_create_delete_event(data, "create"),
    "delete": lambda data: parse_create_delete_event(data, "delete"),
    
    # 배포
    "deployment": parse_deployment_event,
    "deployment_status": parse_deployment_status_event,
    "deployment_protection_rule": parse_deployment_protection_rule_event,
    "deployment_review": parse_deployment_review_event,
    
    # 이슈 및 PR
    "issues": parse_issues_event,
    "issue_comment": parse_issue_comment_event,
    "pull_request": parse_pull_request_event,
    "pull_request_review": parse_pull_request_review_event,
    "pull_request_review_comment": parse_pull_request_review_comment_event,
    
    # 리포지토리
    "fork": parse_fork_event,
    "repository": parse_repository_event,
    "public": parse_public_event,
    
    # Wiki 및 Discussion
    "gollum": parse_gollum_event,
    "discussion": parse_discussion_event,
    "discussion_comment": parse_discussion_comment_event,
    
    # GitHub 앱
    "github_app_authorization": lambda data: parse_github_app_event(data, "github_app_authorization"),
    "installation": lambda data: parse_github_app_event(data, "installation"),
    "installation_repositories": lambda data: parse_github_app_event(data, "installation_repositories"),
}

# 이슈 관련 이벤트 (is_issue=True로 설정해야 하는 이벤트들)
ISSUE_EVENTS = {"issues", "issue_comment"}

@app.route("/webhook", methods=["POST"])
def webhook():
    """
    GitHub webhook 엔드포인트
    
    지원하는 이벤트:
    - ping: 웹훅 등록 테스트
    - push: 코드 푸시
    - pull_request: PR 생성/수정/닫힘
    - pull_request_review: PR 리뷰
    - pull_request_review_comment: PR 리뷰 댓글
    - issues: 이슈 생성/수정/닫힘
    - issue_comment: 이슈 댓글
    - discussion: 토론 생성/수정/삭제 등
    - discussion_comment: 토론 댓글
    - branch_protection_rule: 브랜치 보호 규칙
    - branch_protection_configuration: 브랜치 보호 설정
    - check_run: CI/CD 체크 실행
    - check_suite: CI/CD 체크 스위트
    - code_scanning_alert: 코드 스캔 알림
    - dependabot_alert: Dependabot 알림
    - commit_comment: 커밋 댓글
    - create: 브랜치/태그 생성
    - delete: 브랜치/태그 삭제
    - deployment: 배포
    - deployment_status: 배포 상태
    - deployment_protection_rule: 배포 보호 규칙
    - deployment_review: 배포 검토
    - fork: 저장소 포크
    - repository: 저장소 관련 이벤트
    - public: 저장소 공개 전환
    - gollum: Wiki 페이지 이벤트
    - github_app_authorization: GitHub 앱 인증
    - installation: GitHub 앱 설치
    - installation_repositories: GitHub 앱 저장소
    """
    event_type = request.headers.get("X-GitHub-Event")
    data = request.json

    # 이벤트 타입에 따른 파서 함수 가져오기
    parser = EVENT_PARSERS.get(event_type, parse_other_event)
    
    # 파서 함수 실행
    message = parser(data) if event_type != "other" else parse_other_event(event_type, data)
    
    if message:
        # 이벤트 타입에 따라 적절한 채팅방으로 메시지 전송
        send_telegram_message(message, event_type)
        return jsonify({"status": "success", "message": message})
    
    return jsonify({"status": "ignored", "message": "Unsupported event or action"})

@app.route("/telegram-webhook", methods=["POST"])
def telegram_webhook():
    """
    텔레그램 웹훅 엔드포인트
    봇이 그룹에 초대되었을 때 해당 그룹의 Chat ID를 알려줍니다.
    """
    data = request.json
    
    # 메시지가 없는 경우 무시
    if not data or "message" not in data:
        return jsonify({"status": "ignored"})
    
    message = data["message"]
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    chat_type = chat.get("type")
    
    # /get_chat_id 명령어 처리
    if "text" in message and message["text"] == "/get_chat_id":
        group_info = (
            f"🤖 이 {chat_type}의 Chat ID 정보입니다:\n\n"
            f"Chat ID: <code>{chat_id}</code>\n\n"
            f"이 ID를 .env 파일의 다음 설정에 사용할 수 있습니다:\n"
            f"1. 기본 채팅방으로 설정:\n"
            f"<code>TELEGRAM_DEFAULT_CHAT_ID={chat_id}</code>\n\n"
            f"2. 특정 이벤트 전용 채팅방으로 설정:\n"
            f"<code>EVENT_CHAT_MAPPING={{'\"issues,issue_comment\"': '\"{chat_id}\"'}}</code>"
        )
        send_telegram_message(group_info, "bot_command")
        return jsonify({"status": "success"})
    
    # 새로운 멤버가 추가된 경우
    if "new_chat_members" in message:
        new_members = message["new_chat_members"]
        # 봇이 새로 추가된 멤버인지 확인
        for member in new_members:
            if member.get("username") == TELEGRAM_BOT_USERNAME:
                # 그룹 정보 메시지 생성
                group_info = (
                    f"🤖 안녕하세요! GitHub 알림 봇입니다.\n\n"
                    f"이 {chat_type}의 Chat ID는 <code>{chat_id}</code> 입니다.\n\n"
                    f"이 ID를 .env 파일의 다음 설정에 사용할 수 있습니다:\n"
                    f"1. 기본 채팅방으로 설정:\n"
                    f"<code>TELEGRAM_DEFAULT_CHAT_ID={chat_id}</code>\n\n"
                    f"2. 특정 이벤트 전용 채팅방으로 설정:\n"
                    f"<code>EVENT_CHAT_MAPPING={{'\"issues,issue_comment\"': '\"{chat_id}\"'}}</code>\n\n"
                    f"언제든지 /get_chat_id 명령어를 입력하여 이 정보를 다시 볼 수 있습니다."
                )
                # 그룹에 메시지 전송
                send_telegram_message(group_info, "bot_added")
                return jsonify({"status": "success"})
    
    return jsonify({"status": "ignored"})

def setup_telegram_webhook():
    """
    텔레그램 웹훅을 설정합니다.
    서버 시작 시 자동으로 호출됩니다.
    
    개발 환경을 위한 옵션:
    1. DEVELOPMENT=true로 설정하면 웹훅 설정을 건너뜁니다.
    2. 이 경우 봇이 새 채팅방에 추가되어도 자동으로 Chat ID를 알려주지 않습니다.
    3. 대신 /get_chat_id 명령어를 통해 수동으로 Chat ID를 확인할 수 있습니다.
    """
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not set")
        return

    # 개발 모드 확인
    is_development = os.getenv("DEVELOPMENT", "false").lower() == "true"
    
    # 봇 정보 가져오기
    bot_info_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
    try:
        response = requests.get(bot_info_url)
        response.raise_for_status()
        bot_info = response.json()
        if bot_info["ok"]:
            global TELEGRAM_BOT_USERNAME
            TELEGRAM_BOT_USERNAME = bot_info["result"]["username"]
    except requests.exceptions.RequestException as e:
        print(f"Error getting bot info: {e}")
        return

    if is_development:
        print("Development mode: Skipping webhook setup")
        print(f"You can use the /get_chat_id command in Telegram to get the chat ID")
        return

    # 웹훅 설정
    webhook_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"
    server_url = os.getenv("SERVER_URL")
    
    if not server_url:
        print("Warning: SERVER_URL not set, skipping Telegram webhook setup")
        print("You can use the /get_chat_id command in Telegram to get the chat ID")
        return
        
    if not server_url.startswith("https://"):
        print("Warning: SERVER_URL must use HTTPS. Telegram requires HTTPS for webhooks.")
        print("Consider using a reverse proxy with HTTPS or ngrok for development.")
        print("For now, you can use the /get_chat_id command in Telegram to get the chat ID")
        return
        
    webhook_data = {
        "url": f"{server_url}/telegram-webhook"
    }
    
    try:
        response = requests.post(webhook_url, json=webhook_data)
        response.raise_for_status()
        print("Telegram webhook setup successful")
    except requests.exceptions.RequestException as e:
        print(f"Error setting up Telegram webhook: {e}")

if __name__ == "__main__":
    # 서버 시작 시 텔레그램 웹훅 설정
    setup_telegram_webhook()
    app.run(host="0.0.0.0", port=8080)
