from flask import Flask, request, jsonify
import hmac
import hashlib
import json
import asyncio

from ..config import logger
from ..bot.telegram_bot import send_telegram_message
from .parsers import (
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
    parse_secret_scanning_alert_event
)

# Flask 앱 초기화
app = Flask(__name__)

# 이벤트 타입 그룹화
ISSUE_EVENTS = {"issues", "issue_comment"}
PR_EVENTS = {"pull_request", "pull_request_review", "pull_request_review_comment"}
DISCUSSION_EVENTS = {"discussion", "discussion_comment"}
SECURITY_EVENTS = {"dependabot_alert", "code_scanning_alert", "secret_scanning_alert"}

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

        # 이벤트 타입에 따라 적절한 파서 호출
        message = None
        if event_type == "push":
            message = parse_push_event(payload)
        elif event_type == "pull_request":
            message = parse_pull_request_event(payload)
        elif event_type == "issues":
            message = parse_issues_event(payload)
        elif event_type == "issue_comment":
            message = parse_issue_comment_event(payload)
        elif event_type == "pull_request_review":
            message = parse_pull_request_review_event(payload)
        elif event_type == "pull_request_review_comment":
            message = parse_pull_request_review_comment_event(payload)
        elif event_type == "discussion":
            message = parse_discussion_event(payload)
        elif event_type == "discussion_comment":
            message = parse_discussion_comment_event(payload)
        elif event_type == "dependabot_alert":
            message = parse_dependabot_alert_event(payload)
        elif event_type == "code_scanning_alert":
            message = parse_code_scanning_alert_event(payload)
        elif event_type == "secret_scanning_alert":
            message = parse_secret_scanning_alert_event(payload)

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
