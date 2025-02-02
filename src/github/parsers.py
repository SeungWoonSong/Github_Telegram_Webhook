from ..utils.markdown import escape_markdown_v2, truncate_text
from ..config import logger

def parse_push_event(payload):
    """GitHub push 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        repository = payload.get("repository", {}).get("full_name", "")
        ref = payload.get("ref", "").replace("refs/heads/", "")
        pusher = payload.get("pusher", {}).get("name", "")
        commits = payload.get("commits", [])
        
        if not commits:
            return None
            
        message = f"🔨 *Push to {repository}*\n"
        message += f"*Branch:* `{ref}`\n"
        message += f"*By:* `{pusher}`\n\n"
        
        for commit in commits[:5]:  # 최대 5개 커밋만 표시
            commit_msg = commit.get("message", "").split("\n")[0]  # 첫 줄만 사용
            commit_url = commit.get("url", "")
            commit_id = commit.get("id", "")[:7]  # short SHA
            
            message += f"• [`{commit_id}`]({commit_url}): {commit_msg}\n"
            
        if len(commits) > 5:
            message += f"\n_...and {len(commits) - 5} more commits_"
            
        return message
    except Exception as e:
        logger.error(f"Error parsing push event: {e}")
        return None

def parse_pull_request_event(payload):
    """GitHub pull request 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        action = payload.get("action")
        pr = payload.get("pull_request", {})
        repository = payload.get("repository", {}).get("full_name", "")
        
        if not pr:
            return None
            
        title = pr.get("title", "")
        number = pr.get("number", "")
        user = pr.get("user", {}).get("login", "")
        html_url = pr.get("html_url", "")
        body = pr.get("body", "")
        
        if action in ["opened", "closed", "reopened"]:
            status_emoji = {
                "opened": "🟢",
                "closed": "🔴",
                "reopened": "🔄"
            }.get(action, "")
            
            message = (
                f"{status_emoji} *Pull Request {action} in {repository}*\n"
                f"*#{number}:* [{title}]({html_url})\n"
                f"*By:* `{user}`\n\n"
            )
            
            if body and action == "opened":
                message += "_Description:_\n"
                message += truncate_text(body, 200) + "\n"
                
            if action == "closed" and pr.get("merged"):
                message = message.replace("🔴", "🟣")  # 병합된 경우 다른 이모지 사용
                message = message.replace("closed", "merged")
                
            return message
            
    except Exception as e:
        logger.error(f"Error parsing pull request event: {e}")
        return None

def parse_issues_event(payload):
    """GitHub issues 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        action = payload.get("action")
        issue = payload.get("issue", {})
        repository = payload.get("repository", {}).get("full_name", "")
        
        if not issue or action not in ["opened", "closed", "reopened"]:
            return None
            
        title = issue.get("title", "")
        number = issue.get("number", "")
        user = issue.get("user", {}).get("login", "")
        html_url = issue.get("html_url", "")
        body = issue.get("body", "")
        
        status_emoji = {
            "opened": "🟢",
            "closed": "🔴",
            "reopened": "🔄"
        }.get(action, "")
        
        message = (
            f"{status_emoji} *Issue {action} in {repository}*\n"
            f"*#{number}:* [{title}]({html_url})\n"
            f"*By:* `{user}`\n\n"
        )
        
        if body and action == "opened":
            message += "_Description:_\n"
            message += truncate_text(body, 200) + "\n"
            
        return message
        
    except Exception as e:
        logger.error(f"Error parsing issues event: {e}")
        return None

def parse_issue_comment_event(payload):
    """GitHub issue comment 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        action = payload.get("action")
        if action != "created":
            return None
            
        comment = payload.get("comment", {})
        issue = payload.get("issue", {})
        repository = payload.get("repository", {}).get("full_name", "")
        
        if not comment or not issue:
            return None
            
        user = comment.get("user", {}).get("login", "")
        body = comment.get("body", "")
        html_url = comment.get("html_url", "")
        issue_title = issue.get("title", "")
        issue_number = issue.get("number", "")
        
        message = (
            f"💬 *New comment on {repository}*\n"
            f"*Issue #{issue_number}:* [{issue_title}]({html_url})\n"
            f"*By:* `{user}`\n\n"
        )
        
        if body:
            message += "_Comment:_\n"
            message += truncate_text(body, 200) + "\n"
            
        return message
        
    except Exception as e:
        logger.error(f"Error parsing issue comment event: {e}")
        return None

def parse_pull_request_review_event(payload):
    """GitHub pull request review 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        action = payload.get("action")
        review = payload.get("review", {})
        pr = payload.get("pull_request", {})
        repository = payload.get("repository", {}).get("full_name", "")
        
        if not review or not pr or action != "submitted":
            return None
            
        state = review.get("state", "").lower()
        if state not in ["approved", "changes_requested", "commented"]:
            return None
            
        reviewer = review.get("user", {}).get("login", "")
        body = review.get("body", "")
        html_url = review.get("html_url", "")
        pr_title = pr.get("title", "")
        pr_number = pr.get("number", "")
        
        state_emoji = {
            "approved": "✅",
            "changes_requested": "❌",
            "commented": "💭"
        }.get(state, "")
        
        message = (
            f"{state_emoji} *Pull Request Review in {repository}*\n"
            f"*PR #{pr_number}:* [{pr_title}]({html_url})\n"
            f"*Reviewer:* `{reviewer}`\n"
            f"*Status:* {state}\n\n"
        )
        
        if body:
            message += "_Review comment:_\n"
            message += truncate_text(body, 200) + "\n"
            
        return message
        
    except Exception as e:
        logger.error(f"Error parsing pull request review event: {e}")
        return None

def parse_pull_request_review_comment_event(payload):
    """GitHub pull request review comment 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        action = payload.get("action")
        comment = payload.get("comment", {})
        pr = payload.get("pull_request", {})
        repository = payload.get("repository", {}).get("full_name", "")
        
        if not comment or not pr or action != "created":
            return None
            
        user = comment.get("user", {}).get("login", "")
        body = comment.get("body", "")
        html_url = comment.get("html_url", "")
        pr_title = pr.get("title", "")
        pr_number = pr.get("number", "")
        path = comment.get("path", "")
        position = comment.get("position", "")
        
        message = (
            f"💬 *New review comment on {repository}*\n"
            f"*PR #{pr_number}:* [{pr_title}]({html_url})\n"
            f"*By:* `{user}`\n"
            f"*File:* `{path}`\n"
        )
        
        if position:
            message += f"*Line:* `{position}`\n"
            
        if body:
            message += "\n_Comment:_\n"
            message += truncate_text(body, 200) + "\n"
            
        return message
        
    except Exception as e:
        logger.error(f"Error parsing pull request review comment event: {e}")
        return None

def parse_discussion_event(payload):
    """GitHub discussion 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        action = payload.get("action")
        discussion = payload.get("discussion", {})
        repository = payload.get("repository", {}).get("full_name", "")
        
        if not discussion or action not in ["created", "closed", "reopened"]:
            return None
            
        title = discussion.get("title", "")
        number = discussion.get("number", "")
        user = discussion.get("user", {}).get("login", "")
        html_url = discussion.get("html_url", "")
        body = discussion.get("body", "")
        category = discussion.get("category", {}).get("name", "")
        
        status_emoji = {
            "created": "🟢",
            "closed": "🔴",
            "reopened": "🔄"
        }.get(action, "")
        
        message = (
            f"{status_emoji} *Discussion {action} in {repository}*\n"
            f"*#{number}:* [{title}]({html_url})\n"
            f"*By:* `{user}`\n"
            f"*Category:* {category}\n\n"
        )
        
        if body and action == "created":
            message += "_Description:_\n"
            message += truncate_text(body, 200) + "\n"
            
        return message
        
    except Exception as e:
        logger.error(f"Error parsing discussion event: {e}")
        return None

def parse_discussion_comment_event(payload):
    """GitHub discussion comment 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        action = payload.get("action")
        comment = payload.get("comment", {})
        discussion = payload.get("discussion", {})
        repository = payload.get("repository", {}).get("full_name", "")
        
        if not comment or not discussion or action != "created":
            return None
            
        user = comment.get("user", {}).get("login", "")
        body = comment.get("body", "")
        html_url = comment.get("html_url", "")
        discussion_title = discussion.get("title", "")
        discussion_number = discussion.get("number", "")
        
        message = (
            f"💬 *New comment on discussion in {repository}*\n"
            f"*Discussion #{discussion_number}:* [{discussion_title}]({html_url})\n"
            f"*By:* `{user}`\n\n"
        )
        
        if body:
            message += "_Comment:_\n"
            message += truncate_text(body, 200) + "\n"
            
        return message
        
    except Exception as e:
        logger.error(f"Error parsing discussion comment event: {e}")
        return None

def parse_dependabot_alert_event(payload):
    """GitHub Dependabot alert 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        action = payload.get("action")
        alert = payload.get("alert", {})
        repository = payload.get("repository", {}).get("full_name", "")
        
        if not alert:
            return None
            
        package_name = alert.get("dependency", {}).get("package", {}).get("name", "")
        severity = alert.get("security_vulnerability", {}).get("severity", "")
        affected_range = alert.get("security_vulnerability", {}).get("vulnerable_version_range", "")
        html_url = alert.get("html_url", "")
        
        status_emoji = {
            "created": "🚨",
            "fixed": "✅",
            "dismissed": "🚫"
        }.get(action, "⚠️")
        
        message = (
            f"{status_emoji} *Dependabot Alert {action} in {repository}*\n"
            f"*Package:* `{package_name}`\n"
            f"*Severity:* {severity}\n"
            f"*Affected versions:* `{affected_range}`\n"
            f"*Details:* [View alert]({html_url})\n"
        )
        
        return message
        
    except Exception as e:
        logger.error(f"Error parsing dependabot alert event: {e}")
        return None

def parse_code_scanning_alert_event(payload):
    """GitHub Code Scanning alert 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        action = payload.get("action")
        alert = payload.get("alert", {})
        repository = payload.get("repository", {}).get("full_name", "")
        
        if not alert:
            return None
            
        rule_id = alert.get("rule", {}).get("id", "")
        severity = alert.get("rule", {}).get("severity", "")
        html_url = alert.get("html_url", "")
        
        status_emoji = {
            "created": "🚨",
            "fixed": "✅",
            "closed": "🚫"
        }.get(action, "⚠️")
        
        message = (
            f"{status_emoji} *Code Scanning Alert {action} in {repository}*\n"
            f"*Rule:* `{rule_id}`\n"
            f"*Severity:* {severity}\n"
            f"*Details:* [View alert]({html_url})\n"
        )
        
        return message
        
    except Exception as e:
        logger.error(f"Error parsing code scanning alert event: {e}")
        return None

def parse_secret_scanning_alert_event(payload):
    """GitHub Secret Scanning alert 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        action = payload.get("action")
        alert = payload.get("alert", {})
        repository = payload.get("repository", {}).get("full_name", "")
        
        if not alert:
            return None
            
        secret_type = alert.get("secret_type", "")
        html_url = alert.get("html_url", "")
        
        status_emoji = {
            "created": "🚨",
            "resolved": "✅",
            "reopened": "🔄"
        }.get(action, "⚠️")
        
        message = (
            f"{status_emoji} *Secret Scanning Alert {action} in {repository}*\n"
            f"*Secret Type:* `{secret_type}`\n"
            f"*Details:* [View alert]({html_url})\n"
        )
        
        return message
        
    except Exception as e:
        logger.error(f"Error parsing secret scanning alert event: {e}")
        return None
