import requests
import json
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 서버 설정
SERVER_URL = os.getenv("TEST_SERVER_URL", "http://localhost:8080")
WEBHOOK_URL = f"{SERVER_URL}/webhook"

def send_test_event(event_type, payload):
    """
    테스트 이벤트를 서버로 전송합니다.
    
    Args:
        event_type (str): GitHub 웹훅 이벤트 타입
        payload (dict): 이벤트 페이로드
    """
    headers = {
        "X-GitHub-Event": event_type,
        "Content-Type": "application/json"
    }
    
    response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
    print(f"\n[{event_type}] Response: {response.status_code}")
    print(response.json())

# 테스트 이벤트 페이로드
TEST_EVENTS = {
    # Ping 이벤트
    "ping": {
        "zen": "Testing is important",
        "hook_id": 12345,
        "repository": {
            "full_name": "user/repo"
        }
    },
    
    # Push 이벤트
    "push": {
        "ref": "refs/heads/main",
        "repository": {
            "full_name": "user/repo"
        },
        "commits": [{
            "id": "1234567890abcdef",
            "message": "테스트 커밋",
            "author": {
                "name": "Test User"
            }
        }]
    },
    
    # Issue 이벤트
    "issues": {
        "action": "opened",
        "issue": {
            "number": 1,
            "title": "테스트 이슈",
            "body": "이슈 내용입니다",
            "html_url": "https://github.com/user/repo/issues/1",
            "user": {
                "login": "testuser"
            }
        },
        "repository": {
            "full_name": "user/repo"
        }
    },
    
    # Issue Comment 이벤트
    "issue_comment": {
        "action": "created",
        "issue": {
            "number": 1,
            "title": "테스트 이슈"
        },
        "comment": {
            "body": "테스트 댓글입니다",
            "html_url": "https://github.com/user/repo/issues/1#comment-1",
            "user": {
                "login": "testuser"
            }
        },
        "repository": {
            "full_name": "user/repo"
        }
    },
    
    # Pull Request 이벤트
    "pull_request": {
        "action": "opened",
        "pull_request": {
            "number": 1,
            "title": "테스트 PR",
            "body": "PR 내용입니다",
            "html_url": "https://github.com/user/repo/pull/1",
            "user": {
                "login": "testuser"
            }
        },
        "repository": {
            "full_name": "user/repo"
        }
    },
    
    # PR Review 이벤트
    "pull_request_review": {
        "action": "submitted",
        "review": {
            "state": "approved",
            "body": "LGTM!",
            "html_url": "https://github.com/user/repo/pull/1#pullrequestreview-1",
            "user": {
                "login": "testuser"
            }
        },
        "pull_request": {
            "number": 1,
            "title": "테스트 PR"
        },
        "repository": {
            "full_name": "user/repo"
        }
    },
    
    # PR Review Comment 이벤트
    "pull_request_review_comment": {
        "action": "created",
        "comment": {
            "body": "코드 리뷰 댓글입니다",
            "html_url": "https://github.com/user/repo/pull/1#discussion_r1",
            "user": {
                "login": "testuser"
            }
        },
        "pull_request": {
            "number": 1,
            "title": "테스트 PR"
        },
        "repository": {
            "full_name": "user/repo"
        }
    },
    
    # Discussion 이벤트
    "discussion": {
        "action": "created",
        "discussion": {
            "number": 1,
            "title": "테스트 Discussion",
            "body": "Discussion 내용입니다",
            "html_url": "https://github.com/user/repo/discussions/1",
            "user": {
                "login": "testuser"
            }
        },
        "repository": {
            "full_name": "user/repo"
        }
    },
    
    # Discussion Comment 이벤트
    "discussion_comment": {
        "action": "created",
        "discussion": {
            "number": 1,
            "title": "테스트 Discussion"
        },
        "comment": {
            "body": "Discussion 댓글입니다",
            "html_url": "https://github.com/user/repo/discussions/1#comment-1",
            "user": {
                "login": "testuser"
            }
        },
        "repository": {
            "full_name": "user/repo"
        }
    },
    
    # Branch Protection Rule 이벤트
    "branch_protection_rule": {
        "action": "created",
        "rule": {
            "name": "main",
            "repository": {
                "full_name": "user/repo"
            }
        }
    },
    
    # Check Run 이벤트
    "check_run": {
        "action": "completed",
        "check_run": {
            "name": "테스트",
            "conclusion": "success",
            "html_url": "https://github.com/user/repo/runs/1",
            "repository": {
                "full_name": "user/repo"
            }
        }
    },
    
    # Deployment 이벤트
    "deployment": {
        "action": "created",
        "deployment": {
            "environment": "production",
            "repository": {
                "full_name": "user/repo"
            }
        }
    },
    
    # Fork 이벤트
    "fork": {
        "forkee": {
            "full_name": "user2/repo-fork",
            "html_url": "https://github.com/user2/repo-fork"
        },
        "repository": {
            "full_name": "user/repo"
        }
    },
    
    # Repository 이벤트
    "repository": {
        "action": "created",
        "repository": {
            "full_name": "user/new-repo",
            "html_url": "https://github.com/user/new-repo",
            "description": "새로운 저장소입니다"
        }
    }
}

def test_all_events():
    """모든 이벤트를 테스트합니다."""
    print("🚀 GitHub 웹훅 이벤트 테스트 시작\n")
    
    for event_type, payload in TEST_EVENTS.items():
        print(f"Testing {event_type} event...")
        send_test_event(event_type, payload)
    
    print("\n✅ 모든 테스트 완료")

def test_specific_event(event_type):
    """특정 이벤트만 테스트합니다."""
    if event_type not in TEST_EVENTS:
        print(f"❌ 에러: {event_type} 이벤트를 찾을 수 없습니다")
        print(f"사용 가능한 이벤트: {', '.join(TEST_EVENTS.keys())}")
        return
    
    print(f"🚀 {event_type} 이벤트 테스트 시작\n")
    send_test_event(event_type, TEST_EVENTS[event_type])
    print("\n✅ 테스트 완료")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 특정 이벤트 테스트
        test_specific_event(sys.argv[1])
    else:
        # 모든 이벤트 테스트
        test_all_events()
