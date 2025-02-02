from flask import Flask, request, jsonify
import hmac
import hashlib
import json
import asyncio

from ..config import logger
from ..bot.telegram_bot import send_telegram_message
from .parsers import (
    parse_ping_event,
    parse_push_event,
    parse_pull_request_event,
    parse_issues_event,
    parse_issue_comment_event,
    parse_pull_request_review_event,
    parse_pull_request_review_comment_event,
    parse_discussion_event,
    parse_discussion_comment_event,
    parse_dependabot_alert_event,
    parse_code_scanning_alert_event,
    parse_secret_scanning_alert_event,
    parse_repository_vulnerability_alert_event,
    parse_create_event,
    parse_delete_event,
    parse_release_event,
    parse_package_event,
    parse_deployment_event,
    parse_deployment_status_event,
    parse_fork_event,
    parse_gollum_event,
    parse_member_event,
    parse_project_event,
    parse_project_card_event,
    parse_project_column_event,
    parse_star_event,
    parse_status_event,
    parse_team_add_event,
    parse_watch_event,
    parse_workflow_run_event,
    parse_workflow_job_event,
    parse_check_run_event,
    parse_check_suite_event
)

# Flask 앱 초기화
app = Flask(__name__)

# 이벤트 타입 그룹화
ISSUE_EVENTS = {"issues", "issue_comment"}
PR_EVENTS = {"pull_request", "pull_request_review", "pull_request_review_comment"}
DISCUSSION_EVENTS = {"discussion", "discussion_comment"}
SECURITY_EVENTS = {
    "dependabot_alert", 
    "code_scanning_alert", 
    "secret_scanning_alert",
    "repository_vulnerability_alert"
}
BRANCH_EVENTS = {"create", "delete"}
RELEASE_EVENTS = {"release"}
PACKAGE_EVENTS = {"package"}
DEPLOYMENT_EVENTS = {"deployment", "deployment_status"}
FORK_EVENTS = {"fork"}
GOLLUM_EVENTS = {"gollum"}  # Wiki 이벤트
MEMBER_EVENTS = {"member"}
PROJECT_EVENTS = {"project", "project_card", "project_column"}
STAR_EVENTS = {"star"}
STATUS_EVENTS = {"status"}
TEAM_EVENTS = {"team_add"}
WATCH_EVENTS = {"watch"}
WORKFLOW_EVENTS = {"workflow_run", "workflow_job", "check_run", "check_suite"}

# 이벤트 타입별 파서 매핑
EVENT_PARSERS = {
    # PING
    "ping": parse_ping_event,
    # 기본 이벤트
    "push": parse_push_event,
    
    # 이슈 관련 이벤트
    "issues": parse_issues_event,
    "issue_comment": parse_issue_comment_event,
    
    # PR 관련 이벤트
    "pull_request": parse_pull_request_event,
    "pull_request_review": parse_pull_request_review_event,
    "pull_request_review_comment": parse_pull_request_review_comment_event,
    
    # 토론 관련 이벤트
    "discussion": parse_discussion_event,
    "discussion_comment": parse_discussion_comment_event,
    
    # 보안 관련 이벤트
    "dependabot_alert": parse_dependabot_alert_event,
    "code_scanning_alert": parse_code_scanning_alert_event,
    "secret_scanning_alert": parse_secret_scanning_alert_event,
    "repository_vulnerability_alert": parse_repository_vulnerability_alert_event,
    
    # 브랜치/태그 관련 이벤트
    "create": parse_create_event,
    "delete": parse_delete_event,
    
    # 릴리즈/패키지 관련 이벤트
    "release": parse_release_event,
    "package": parse_package_event,
    
    # 배포 관련 이벤트
    "deployment": parse_deployment_event,
    "deployment_status": parse_deployment_status_event,
    
    # 저장소 관련 이벤트
    "fork": parse_fork_event,
    "gollum": parse_gollum_event,
    "member": parse_member_event,
    "star": parse_star_event,
    "status": parse_status_event,
    "team_add": parse_team_add_event,
    "watch": parse_watch_event,
    
    # 프로젝트 관련 이벤트
    "project": parse_project_event,
    "project_card": parse_project_card_event,
    "project_column": parse_project_column_event,
    
    # 워크플로우/체크 관련 이벤트
    "workflow_run": parse_workflow_run_event,
    "workflow_job": parse_workflow_job_event,
    "check_run": parse_check_run_event,
    "check_suite": parse_check_suite_event
}

@app.route("/webhook", methods=["POST"])
def webhook():
    """
    GitHub webhook 엔드포인트
    """
    try:
        # GitHub 이벤트 타입 확인
        event_type = request.headers.get("X-GitHub-Event")
        if not event_type:
            return jsonify({"status": "error", "message": "No X-GitHub-Event header"}), 400

        # 요청 본문 파싱
        payload = request.json
        if not payload:
            return jsonify({"status": "error", "message": "No payload"}), 400

        # 이벤트 타입에 맞는 파서 호출
        parser = EVENT_PARSERS.get(event_type)
        if parser:
            message = parser(payload)
            if message:
                # 이벤트 타입에 따라 적절한 채팅방으로 메시지 전송
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(send_telegram_message(message, event_type))
                loop.close()
                return jsonify({"status": "success", "message": message})

        return jsonify({"status": "ignored", "message": "Unsupported event or action"})

    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
