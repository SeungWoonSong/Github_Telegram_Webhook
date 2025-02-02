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

def parse_repository_vulnerability_alert_event(payload):
    """GitHub Repository Vulnerability Alert 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        action = payload.get("action")
        alert = payload.get("alert", {})
        repository = payload.get("repository", {}).get("full_name", "")
        
        if not alert:
            return None
            
        affected_package = alert.get("affected_package_name", "")
        affected_range = alert.get("affected_range", "")
        external_reference = alert.get("external_reference", "")
        
        status_emoji = {
            "create": "🚨",
            "resolve": "✅",
            "dismiss": "🚫"
        }.get(action, "⚠️")
        
        message = (
            f"{status_emoji} *Repository Vulnerability Alert {action} in {repository}*\n"
            f"*Package:* `{affected_package}`\n"
            f"*Affected versions:* `{affected_range}`\n"
        )
        
        if external_reference:
            message += f"*Reference:* [View details]({external_reference})\n"
            
        return message
        
    except Exception as e:
        logger.error(f"Error parsing repository vulnerability alert event: {e}")
        return None

def parse_create_event(payload):
    """GitHub Create 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        ref_type = payload.get("ref_type")
        ref = payload.get("ref")
        repository = payload.get("repository", {}).get("full_name", "")
        
        message = (
            f"🌱 *New {ref_type} created in {repository}*\n"
            f"*Name:* `{ref}`\n"
        )
        
        return message
        
    except Exception as e:
        logger.error(f"Error parsing create event: {e}")
        return None

def parse_delete_event(payload):
    """GitHub Delete 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        ref_type = payload.get("ref_type")
        ref = payload.get("ref")
        repository = payload.get("repository", {}).get("full_name", "")
        
        message = (
            f"🗑️ *{ref_type} deleted in {repository}*\n"
            f"*Name:* `{ref}`\n"
        )
        
        return message
        
    except Exception as e:
        logger.error(f"Error parsing delete event: {e}")
        return None

def parse_release_event(payload):
    """GitHub Release 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        action = payload.get("action")
        release = payload.get("release", {})
        repository = payload.get("repository", {}).get("full_name", "")
        
        if not release or action not in ["published", "created", "edited"]:
            return None
            
        tag = release.get("tag_name", "")
        name = release.get("name", "")
        body = release.get("body", "")
        html_url = release.get("html_url", "")
        
        message = (
            f"📦 *Release {action} in {repository}*\n"
            f"*Version:* [{tag}]({html_url})\n"
        )
        
        if name:
            message += f"*Name:* {name}\n"
            
        if body and action in ["published", "created"]:
            message += "\n_Release notes:_\n"
            message += truncate_text(body, 200) + "\n"
            
        return message
        
    except Exception as e:
        logger.error(f"Error parsing release event: {e}")
        return None

def parse_package_event(payload):
    """GitHub Package 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        action = payload.get("action")
        package = payload.get("package", {})
        repository = payload.get("repository", {}).get("full_name", "")
        
        if not package:
            return None
            
        package_name = package.get("name", "")
        package_type = package.get("package_type", "")
        html_url = package.get("html_url", "")
        
        message = (
            f"📦 *Package {action} in {repository}*\n"
            f"*Name:* [{package_name}]({html_url})\n"
            f"*Type:* {package_type}\n"
        )
        
        return message
        
    except Exception as e:
        logger.error(f"Error parsing package event: {e}")
        return None

def parse_deployment_event(payload):
    """GitHub Deployment 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        deployment = payload.get("deployment", {})
        repository = payload.get("repository", {}).get("full_name", "")
        
        if not deployment:
            return None
            
        environment = deployment.get("environment", "")
        ref = deployment.get("ref", "")
        
        message = (
            f"🚀 *New deployment in {repository}*\n"
            f"*Environment:* `{environment}`\n"
            f"*Ref:* `{ref}`\n"
        )
        
        return message
        
    except Exception as e:
        logger.error(f"Error parsing deployment event: {e}")
        return None

def parse_deployment_status_event(payload):
    """GitHub Deployment Status 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        deployment_status = payload.get("deployment_status", {})
        deployment = payload.get("deployment", {})
        repository = payload.get("repository", {}).get("full_name", "")
        
        if not deployment_status or not deployment:
            return None
            
        state = deployment_status.get("state", "")
        environment = deployment.get("environment", "")
        
        status_emoji = {
            "success": "✅",
            "failure": "❌",
            "error": "⚠️",
            "pending": "⏳"
        }.get(state, "ℹ️")
        
        message = (
            f"{status_emoji} *Deployment status update in {repository}*\n"
            f"*Environment:* `{environment}`\n"
            f"*Status:* {state}\n"
        )
        
        return message
        
    except Exception as e:
        logger.error(f"Error parsing deployment status event: {e}")
        return None

def parse_fork_event(payload):
    """GitHub Fork 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        forkee = payload.get("forkee", {})
        repository = payload.get("repository", {}).get("full_name", "")
        
        if not forkee:
            return None
            
        fork_owner = forkee.get("owner", {}).get("login", "")
        fork_name = forkee.get("full_name", "")
        html_url = forkee.get("html_url", "")
        
        message = (
            f"🍴 *New fork of {repository}*\n"
            f"*Forked to:* [{fork_name}]({html_url})\n"
            f"*By:* `{fork_owner}`\n"
        )
        
        return message
        
    except Exception as e:
        logger.error(f"Error parsing fork event: {e}")
        return None

def parse_gollum_event(payload):
    """GitHub Wiki (Gollum) 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        pages = payload.get("pages", [])
        repository = payload.get("repository", {}).get("full_name", "")
        
        if not pages:
            return None
            
        message = f"📚 *Wiki updated in {repository}*\n\n"
        
        for page in pages[:5]:  # 최대 5개 페이지만 표시
            action = page.get("action", "")
            title = page.get("title", "")
            html_url = page.get("html_url", "")
            
            message += f"• {action}: [{title}]({html_url})\n"
            
        if len(pages) > 5:
            message += f"\n_...and {len(pages) - 5} more pages_"
            
        return message
        
    except Exception as e:
        logger.error(f"Error parsing gollum event: {e}")
        return None

def parse_member_event(payload):
    """GitHub Member 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        action = payload.get("action")
        member = payload.get("member", {})
        repository = payload.get("repository", {}).get("full_name", "")
        
        if not member:
            return None
            
        username = member.get("login", "")
        html_url = member.get("html_url", "")
        
        message = (
            f"👥 *Repository member {action} in {repository}*\n"
            f"*User:* [{username}]({html_url})\n"
        )
        
        return message
        
    except Exception as e:
        logger.error(f"Error parsing member event: {e}")
        return None

def parse_project_event(payload):
    """GitHub Project 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        action = payload.get("action")
        project = payload.get("project", {})
        repository = payload.get("repository", {}).get("full_name", "")
        
        if not project:
            return None
            
        name = project.get("name", "")
        html_url = project.get("html_url", "")
        body = project.get("body", "")
        
        message = (
            f"📋 *Project {action} in {repository}*\n"
            f"*Name:* [{name}]({html_url})\n"
        )
        
        if body and action == "created":
            message += "_Description:_\n"
            message += truncate_text(body, 200) + "\n"
            
        return message
        
    except Exception as e:
        logger.error(f"Error parsing project event: {e}")
        return None

def parse_project_card_event(payload):
    """GitHub Project Card 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        action = payload.get("action")
        card = payload.get("project_card", {})
        repository = payload.get("repository", {}).get("full_name", "")
        
        if not card:
            return None
            
        note = card.get("note", "")
        column_name = payload.get("project_column", {}).get("name", "")
        
        message = (
            f"📑 *Project card {action} in {repository}*\n"
            f"*Column:* `{column_name}`\n"
        )
        
        if note:
            message += f"*Note:* {truncate_text(note, 100)}\n"
            
        return message
        
    except Exception as e:
        logger.error(f"Error parsing project card event: {e}")
        return None

def parse_project_column_event(payload):
    """GitHub Project Column 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        action = payload.get("action")
        column = payload.get("project_column", {})
        repository = payload.get("repository", {}).get("full_name", "")
        
        if not column:
            return None
            
        name = column.get("name", "")
        
        message = (
            f"📊 *Project column {action} in {repository}*\n"
            f"*Name:* `{name}`\n"
        )
        
        return message
        
    except Exception as e:
        logger.error(f"Error parsing project column event: {e}")
        return None

def parse_star_event(payload):
    """GitHub Star 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        action = payload.get("action")
        repository = payload.get("repository", {}).get("full_name", "")
        sender = payload.get("sender", {}).get("login", "")
        
        message = (
            f"⭐ *Repository {action} by {sender}*\n"
            f"*Repository:* `{repository}`\n"
        )
        
        return message
        
    except Exception as e:
        logger.error(f"Error parsing star event: {e}")
        return None

def parse_status_event(payload):
    """GitHub Status 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        state = payload.get("state", "")
        description = payload.get("description", "")
        target_url = payload.get("target_url", "")
        repository = payload.get("repository", {}).get("full_name", "")
        
        status_emoji = {
            "success": "✅",
            "failure": "❌",
            "error": "⚠️",
            "pending": "⏳"
        }.get(state, "ℹ️")
        
        message = (
            f"{status_emoji} *Status update in {repository}*\n"
            f"*Status:* {state}\n"
        )
        
        if description:
            message += f"*Description:* {description}\n"
            
        if target_url:
            message += f"*Details:* [View details]({target_url})\n"
            
        return message
        
    except Exception as e:
        logger.error(f"Error parsing status event: {e}")
        return None

def parse_team_add_event(payload):
    """GitHub Team Add 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        team = payload.get("team", {})
        repository = payload.get("repository", {}).get("full_name", "")
        
        if not team:
            return None
            
        team_name = team.get("name", "")
        team_url = team.get("html_url", "")
        
        message = (
            f"👥 *Team added to {repository}*\n"
            f"*Team:* [{team_name}]({team_url})\n"
        )
        
        return message
        
    except Exception as e:
        logger.error(f"Error parsing team add event: {e}")
        return None

def parse_watch_event(payload):
    """GitHub Watch 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        action = payload.get("action")
        repository = payload.get("repository", {}).get("full_name", "")
        sender = payload.get("sender", {}).get("login", "")
        
        message = (
            f"👀 *Repository {action} by {sender}*\n"
            f"*Repository:* `{repository}`\n"
        )
        
        return message
        
    except Exception as e:
        logger.error(f"Error parsing watch event: {e}")
        return None

def parse_workflow_run_event(payload):
    """GitHub Workflow Run 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        workflow_run = payload.get("workflow_run", {})
        repository = payload.get("repository", {}).get("full_name", "")
        
        if not workflow_run:
            return None
            
        name = workflow_run.get("name", "")
        status = workflow_run.get("status", "")
        conclusion = workflow_run.get("conclusion", "")
        html_url = workflow_run.get("html_url", "")
        
        status_emoji = {
            "completed": "✅" if conclusion == "success" else "❌",
            "in_progress": "⏳",
            "queued": "⌛"
        }.get(status, "ℹ️")
        
        message = (
            f"{status_emoji} *Workflow run in {repository}*\n"
            f"*Workflow:* [{name}]({html_url})\n"
            f"*Status:* {status}\n"
        )
        
        if conclusion:
            message += f"*Conclusion:* {conclusion}\n"
            
        return message
        
    except Exception as e:
        logger.error(f"Error parsing workflow run event: {e}")
        return None

def parse_workflow_job_event(payload):
    """GitHub Workflow Job 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        workflow_job = payload.get("workflow_job", {})
        repository = payload.get("repository", {}).get("full_name", "")
        
        if not workflow_job:
            return None
            
        name = workflow_job.get("name", "")
        status = workflow_job.get("status", "")
        conclusion = workflow_job.get("conclusion", "")
        html_url = workflow_job.get("html_url", "")
        
        status_emoji = {
            "completed": "✅" if conclusion == "success" else "❌",
            "in_progress": "⏳",
            "queued": "⌛"
        }.get(status, "ℹ️")
        
        message = (
            f"{status_emoji} *Workflow job in {repository}*\n"
            f"*Job:* [{name}]({html_url})\n"
            f"*Status:* {status}\n"
        )
        
        if conclusion:
            message += f"*Conclusion:* {conclusion}\n"
            
        return message
        
    except Exception as e:
        logger.error(f"Error parsing workflow job event: {e}")
        return None

def parse_check_run_event(payload):
    """GitHub Check Run 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        action = payload.get("action")
        check_run = payload.get("check_run", {})
        repository = payload.get("repository", {}).get("full_name", "")
        
        if not check_run:
            return None
            
        name = check_run.get("name", "")
        status = check_run.get("status", "")
        conclusion = check_run.get("conclusion", "")
        html_url = check_run.get("html_url", "")
        
        status_emoji = {
            "completed": "✅" if conclusion == "success" else "❌",
            "in_progress": "⏳",
            "queued": "⌛"
        }.get(status, "ℹ️")
        
        message = (
            f"{status_emoji} *Check run {action} in {repository}*\n"
            f"*Check:* [{name}]({html_url})\n"
            f"*Status:* {status}\n"
        )
        
        if conclusion:
            message += f"*Conclusion:* {conclusion}\n"
            
        return message
        
    except Exception as e:
        logger.error(f"Error parsing check run event: {e}")
        return None

def parse_check_suite_event(payload):
    """GitHub Check Suite 이벤트를 파싱하여 메시지를 생성합니다."""
    try:
        action = payload.get("action")
        check_suite = payload.get("check_suite", {})
        repository = payload.get("repository", {}).get("full_name", "")
        
        if not check_suite:
            return None
            
        status = check_suite.get("status", "")
        conclusion = check_suite.get("conclusion", "")
        
        status_emoji = {
            "completed": "✅" if conclusion == "success" else "❌",
            "in_progress": "⏳",
            "queued": "⌛"
        }.get(status, "ℹ️")
        
        message = (
            f"{status_emoji} *Check suite {action} in {repository}*\n"
            f"*Status:* {status}\n"
        )
        
        if conclusion:
            message += f"*Conclusion:* {conclusion}\n"
            
        return message
        
    except Exception as e:
        logger.error(f"Error parsing check suite event: {e}")
        return None
