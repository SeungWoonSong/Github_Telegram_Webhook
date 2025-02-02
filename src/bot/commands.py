from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from ..config import logger

async def get_chat_id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    현재 채팅방의 Chat ID를 반환하는 명령어 핸들러
    """
    chat = update.effective_chat
    chat_id = chat.id
    chat_type = chat.type
    
    logger.info(f"Received /get_chat_id command in chat {chat_id}")
    group_info = (
        f"🤖 안녕하세요! GitHub 알림 봇입니다.\n"
        f"개발자: [Andrew Song](https://www.linkedin.com/in/sungwoonsong/)\n\n"
        f"이 {chat_type}의 Chat ID 정보입니다:\n"
        f"Chat ID: `{chat_id}`\n\n"
        f"이 ID를 .env 파일의 다음 설정에 사용할 수 있습니다:\n"
        f"1. 기본 채팅방으로 설정:\n"
        f"`TELEGRAM_DEFAULT_CHAT_ID={chat_id}`\n\n"
        f"2. 특정 이벤트 전용 채팅방으로 설정:\n"
        f"`EVENT_CHAT_MAPPING={{\\\"issues,issue_comment\\\": \\\"{chat_id}\\\"}}`"
    )
    
    await update.message.reply_text(
        text=group_info,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=False  # 링크 미리보기 활성화
    )
