import asyncio
import threading
from src.config import SERVER_PORT, logger
from src.bot.telegram_bot import start_bot
from src.github.webhook import app

if __name__ == '__main__':
    try:
        # 봇 초기화
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # 봇 시작
        loop.run_until_complete(start_bot())
        
        # Flask 앱 실행
        def run_flask():
            app.run(host='0.0.0.0', port=SERVER_PORT)
        
        # Flask 앱을 별도 스레드에서 실행
        flask_thread = threading.Thread(target=run_flask)
        flask_thread.start()
        
        logger.info(f"Server started on port {SERVER_PORT}")
        
        # 메인 이벤트 루프 실행
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
    except Exception as e:
        logger.error(f"Error starting server: {e}")
    finally:
        loop.close()