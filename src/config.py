import os
import json
import logging
from logging.handlers import RotatingFileHandler

# .env 파일 로드
from dotenv import load_dotenv
load_dotenv()

# 환경 변수
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME")
TELEGRAM_DEFAULT_CHAT_ID = os.getenv("TELEGRAM_DEFAULT_CHAT_ID")
EVENT_CHAT_MAPPING = json.loads(os.getenv("EVENT_CHAT_MAPPING", "{}"))
DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "true").lower() == "true"
SERVER_PORT = int(os.getenv("SERVER_PORT", "8080"))

# 필수 환경변수 검증
required_vars = {
    "TELEGRAM_BOT_TOKEN": "봇 토큰",
    "TELEGRAM_DEFAULT_CHAT_ID": "기본 채팅방 ID",
    "TELEGRAM_BOT_USERNAME": "봇 사용자명"
}

missing_vars = [desc for var, desc in required_vars.items() if not os.getenv(var)]
if missing_vars:
    missing_desc = ", ".join(missing_vars)
    raise ValueError(f"다음 환경변수가 설정되어 있지 않습니다: {missing_desc}")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            'bot.log',
            maxBytes=10485760,  # 10MB
            backupCount=5,
            encoding='utf-8'
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
