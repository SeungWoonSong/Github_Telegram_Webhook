import asyncio
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode

from ..config import (
    TELEGRAM_BOT_TOKEN, TELEGRAM_DEFAULT_CHAT_ID,
    EVENT_CHAT_MAPPING, DEVELOPMENT_MODE, logger
)

# Telegram 봇 초기화
application = None

def get_chat_id_for_event(event_type):
    """
    이벤트 타입에 따른 채팅방 ID를 반환합니다.
    """
    # 이벤트 타입에 해당하는 채팅방 ID 찾기
    for event_types, chat_id in EVENT_CHAT_MAPPING.items():
        if event_type in event_types.split(','):
            return chat_id
            
    # 기본 채팅방 ID 반환
    return TELEGRAM_DEFAULT_CHAT_ID

async def send_telegram_message(message, event_type):
    """
    텔레그램으로 메시지를 전송합니다.
    이벤트 타입에 따라 적절한 채팅방으로 전송됩니다.
    """
    if not TELEGRAM_BOT_TOKEN:
        logger.error("Error: TELEGRAM_BOT_TOKEN not set")
        return
    
    chat_id = get_chat_id_for_event(event_type)
    if not chat_id:
        logger.error(f"Error: No chat ID configured for event type: {event_type}")
        return

    try:
        if application:
            await application.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
        else:
            logger.error("Error: Telegram application not initialized")
    except Exception as e:
        logger.error(f"Error sending message to Telegram: {e}")

async def start_bot():
    """
    텔레그램 봇을 초기화하고 시작합니다.
    """
    global application
    
    if not TELEGRAM_BOT_TOKEN:
        logger.error("Error: TELEGRAM_BOT_TOKEN not set")
        return

    try:
        # 봇 초기화
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # 명령어 핸들러 등록 (commands.py에서 가져옴)
        from .commands import get_chat_id_command
        application.add_handler(CommandHandler("get_chat_id", get_chat_id_command))
        
        # 봇 시작
        await application.initialize()
        if not DEVELOPMENT_MODE:
            # 프로덕션 모드에서는 웹훅 설정
            webhook_url = f"https://your-domain.com/telegram-webhook"
            await application.bot.set_webhook(url=webhook_url)
        else:
            # 개발 모드에서는 폴링 사용
            await application.start()
            logger.info("Development mode: Starting polling...")
            await application.updater.start_polling()
            
    except Exception as e:
        logger.error(f"Error starting Telegram bot: {e}")
