"""
Inspiration Bot - Telegram Notifier
Sends creative ideas to Telegram
"""
import asyncio
from datetime import datetime
from typing import Optional
import pytz
from telegram import Bot
from telegram.error import TelegramError
from loguru import logger

from config import settings


class TelegramNotifier:
    """
    텔레그램 알림 발송 (영감봇 전용)
    """
    
    def __init__(self):
        self.bot: Optional[Bot] = None
        self.chat_id = settings.telegram_chat_id
        self.timezone = pytz.timezone(settings.timezone)
    
    def get_now(self) -> datetime:
        """KST 현재 시간 반환"""
        return datetime.now(self.timezone)
    
    async def start(self):
        """Initialize Telegram bot"""
        try:
            self.bot = Bot(token=settings.telegram_bot_token)
            logger.info("📱 Telegram 봇 초기화 완료")
        except Exception as e:
            logger.error(f"❌ Telegram 봇 초기화 실패: {e}")
            self.bot = None
    
    async def close(self):
        """Cleanup"""
        pass
    
    async def send_message(
        self,
        message: str,
        parse_mode: Optional[str] = "Markdown"
    ) -> bool:
        """메시지 발송"""
        if not self.bot:
            return False
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode
            )
            return True
        except TelegramError as e:
            logger.error(f"❌ Telegram 발송 실패: {e}")
            return False
    
    async def send_idea(self, idea: str) -> bool:
        """
        아이디어 메시지 발송
        
        Args:
            idea: 생성된 아이디어 텍스트
        """
        # 날짜 헤더 추가
        date_str = self.get_now().strftime("%B %d")
        
        # Markdown 형식 그대로 전송 (Gemini가 생성한 형식)
        return await self.send_message(idea, parse_mode="Markdown")


# Test
async def test_notifier():
    """테스트 함수"""
    notifier = TelegramNotifier()
    await notifier.start()
    
    if notifier.bot:
        result = await notifier.send_message("🧪 영감봇 테스트 메시지입니다!")
        print(f"발송 결과: {'성공' if result else '실패'}")
    else:
        print("❌ 봇 초기화 실패")


if __name__ == "__main__":
    asyncio.run(test_notifier())
