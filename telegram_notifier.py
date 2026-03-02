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


# Telegram 메시지 최대 길이
MAX_MESSAGE_LENGTH = 4096


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
        """메시지 발송 (Markdown 실패시 HTML -> 일반 텍스트 fallback)"""
        if not self.bot:
            return False
        
        try:
            # 메시지가 너무 길면 분할 발송
            if len(message) > MAX_MESSAGE_LENGTH:
                return await self._send_long_message(message, parse_mode)
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode
            )
            return True
        except TelegramError as e:
            error_msg = str(e)
            logger.warning(f"⚠️ Markdown 발송 실패, 일반 텍스트로 재시도: {error_msg}")
            
            # Markdown 파싱 에러시 일반 텍스트로 재시도
            if "parse" in error_msg.lower() or "entities" in error_msg.lower():
                try:
                    # Markdown 기호 제거 후 재발송
                    clean_message = self._clean_markdown(message)
                    
                    if len(clean_message) > MAX_MESSAGE_LENGTH:
                        return await self._send_long_message(clean_message, None)
                    
                    await self.bot.send_message(
                        chat_id=self.chat_id,
                        text=clean_message,
                        parse_mode=None
                    )
                    logger.info("✅ 일반 텍스트로 발송 성공")
                    return True
                except TelegramError as e2:
                    logger.error(f"❌ 일반 텍스트 발송도 실패: {e2}")
                    return False
            
            logger.error(f"❌ Telegram 발송 실패: {e}")
            return False
    
    async def _send_long_message(
        self,
        message: str,
        parse_mode: Optional[str]
    ) -> bool:
        """긴 메시지를 분할 발송"""
        # 구분선 기준으로 분할
        parts = message.split("━━━━━━━━━━━━━━━")
        
        if len(parts) <= 1:
            # 구분선이 없으면 글자 수 기준 분할
            parts = [message[i:i+MAX_MESSAGE_LENGTH] 
                     for i in range(0, len(message), MAX_MESSAGE_LENGTH)]
        
        success = True
        current_chunk = ""
        
        for i, part in enumerate(parts):
            separator = "━━━━━━━━━━━━━━━\n" if i > 0 else ""
            candidate = current_chunk + separator + part
            
            if len(candidate) > MAX_MESSAGE_LENGTH:
                # 현재 청크 발송
                if current_chunk.strip():
                    try:
                        await self.bot.send_message(
                            chat_id=self.chat_id,
                            text=current_chunk.strip(),
                            parse_mode=parse_mode
                        )
                    except TelegramError:
                        # Markdown 실패시 일반 텍스트로
                        clean = self._clean_markdown(current_chunk.strip())
                        try:
                            await self.bot.send_message(
                                chat_id=self.chat_id,
                                text=clean,
                                parse_mode=None
                            )
                        except TelegramError as e:
                            logger.error(f"❌ 분할 발송 실패: {e}")
                            success = False
                    await asyncio.sleep(0.5)  # 스팸 방지
                
                current_chunk = separator + part
            else:
                current_chunk = candidate
        
        # 마지막 청크 발송
        if current_chunk.strip():
            try:
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=current_chunk.strip(),
                    parse_mode=parse_mode
                )
            except TelegramError:
                clean = self._clean_markdown(current_chunk.strip())
                try:
                    await self.bot.send_message(
                        chat_id=self.chat_id,
                        text=clean,
                        parse_mode=None
                    )
                except TelegramError as e:
                    logger.error(f"❌ 마지막 분할 발송 실패: {e}")
                    success = False
        
        return success
    
    @staticmethod
    def _clean_markdown(text: str) -> str:
        """Markdown 특수문자 제거하여 일반 텍스트로 변환"""
        # 볼드/이탤릭 기호 제거
        cleaned = text.replace("*", "").replace("_", "").replace("`", "")
        # 링크 형식 [text](url) -> text (url)
        import re
        cleaned = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1 (\2)', cleaned)
        return cleaned
    
    async def send_idea(self, idea: str) -> bool:
        """
        아이디어 메시지 발송
        
        Args:
            idea: 생성된 아이디어 텍스트
        """
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
        print("봇 초기화 실패")


if __name__ == "__main__":
    asyncio.run(test_notifier())
