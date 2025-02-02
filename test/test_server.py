import os
import json
import requests
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def send_test_event(event_type, event_data, webhook_secret=None):
    """
    GitHub 이벤트를 시뮬레이션하여 로컬 서버로 전송합니다.
    
    Args:
        event_type (str): GitHub 이벤트 타입 (예: 'push', 'pull_request', 'issues' 등)
        event_data (dict): 이벤트 데이터
        webhook_secret (str, optional): GitHub webhook secret
    """
    # 서버 URL
    server_url = "http://localhost:8080/webhook"
    
    # 헤더 설정
    headers = {
        "Content-Type": "application/json",
        "X-GitHub-Event": event_type
    }
    
    # Webhook secret이 제공된 경우 서명 생성
    if webhook_secret:
        import hmac
        import hashlib
        
        # 요청 바디를 JSON 문자열로 변환
        body = json.dumps(event_data).encode()
        
        # HMAC-SHA256 서명 생성
        signature = hmac.new(
            webhook_secret.encode(),
            msg=body,
            digestmod=hashlib.sha256
        ).hexdigest()
        
        headers["X-Hub-Signature-256"] = f"sha256={signature}"
    
    try:
        # POST 요청 전송
        response = requests.post(
            server_url,
            headers=headers,
            json=event_data
        )
        
        # 응답 확인
        if response.status_code == 200:
            print(f"✅ 성공: 이벤트가 성공적으로 전송되었습니다.")
            print(f"응답: {response.json()}")
        else:
            print(f"❌ 실패: 서버가 {response.status_code} 상태 코드를 반환했습니다.")
            print(f"응답: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 오류: 요청 전송 중 오류가 발생했습니다: {e}")
        print("서버가 실행 중인지 확인해주세요.")

# 테스트 이벤트 예시들
test_events = {
    # Pull Request 이벤트
    "pull_request": {
        "action": "opened",
        "pull_request": {
            "html_url": "https://github.com/owner/repo/pull/1",
            "title": "테스트 PR",
            "user": {
                "login": "test-user"
            },
            "body": "PR 설명입니다.",
            "base": {
                "ref": "main"
            },
            "head": {
                "ref": "feature-branch"
            }
        },
        "repository": {
            "full_name": "owner/repo"
        }
    },
    
    # Issue 이벤트
    "issues": {
        "action": "opened",
        "issue": {
            "html_url": "https://github.com/owner/repo/issues/1",
            "title": "테스트 이슈",
            "user": {
                "login": "test-user"
            },
            "body": "이슈 설명입니다."
        },
        "repository": {
            "full_name": "owner/repo"
        }
    },
    
    # Push 이벤트
    "push": {
        "ref": "refs/heads/main",
        "before": "0000000000000000000000000000000000000000",
        "after": "1234567890abcdef1234567890abcdef12345678",
        "commits": [
            {
                "id": "1234567890abcdef1234567890abcdef12345678",
                "message": "테스트 커밋",
                "url": "https://github.com/owner/repo/commit/1234567890abcdef1234567890abcdef12345678",
                "author": {
                    "name": "Test User",
                    "email": "test@example.com"
                }
            }
        ],
        "repository": {
            "full_name": "owner/repo"
        },
        "pusher": {
            "name": "test-user"
        }
    }
}

if __name__ == "__main__":
    # 사용 예시
    print("🚀 GitHub 웹훅 테스트 시작")
    print("----------------------------")
    
    # Webhook secret 가져오기 (옵션)
    webhook_secret = os.getenv("WEBHOOK_SECRET")
    
    # 테스트할 이벤트 선택
    for event_type, event_data in test_events.items():
        print(f"\n📦 {event_type.upper()} 이벤트 전송 중...")
        send_test_event(event_type, event_data, webhook_secret)
        print("----------------------------")
