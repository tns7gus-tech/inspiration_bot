"""
Inspiration Bot - Main Entry Point
Daily creative project idea bot + 토양체질 dinner menu recommender
"""
import asyncio
import os
import sys
import signal
from datetime import datetime
import pytz
from pathlib import Path

from aiohttp import web
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

# Add current dir to path
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from idea_generator import IdeaGenerator
from meal_recommender import MealRecommender
from telegram_notifier import TelegramNotifier


# Configure logging
logger.remove()
log_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>"
logger.add(sys.stderr, format=log_format, level=settings.log_level)


class InspirationBot:
    """
    매일 아침 창의적인 프로젝트 아이디어를 보내주는 영감봇
    + 매일 17:30 토양체질 저녁 식단 추천
    """
    
    def __init__(self):
        self.generator = IdeaGenerator()
        self.meal_recommender = MealRecommender()
        self.notifier = TelegramNotifier()
        self.scheduler = AsyncIOScheduler(timezone=pytz.timezone(settings.timezone))
        self.running = False
        
        logger.info("💡 InspirationBot 초기화 완료")
    
    async def start(self):
        """봇 시작"""
        await self.notifier.start()
        
        # 스케줄러 설정 1: 영감봇 (N분마다)
        self.scheduler.add_job(
            self.send_daily_inspiration,
            IntervalTrigger(minutes=settings.send_interval_minutes),
            id="interval_inspiration",
            name="Interval Inspiration Sender"
        )
        
        # 스케줄러 설정 2: 토양체질 저녁 식단 (매일 17:30)
        self.scheduler.add_job(
            self.send_dinner_recommendation,
            CronTrigger(
                hour=settings.meal_send_hour,
                minute=settings.meal_send_minute
            ),
            id="dinner_recommendation",
            name="Daily Dinner Recommendation"
        )
        
        self.scheduler.start()
        
        logger.success(
            f"🚀 영감봇 시작! "
            f"아이디어: {settings.send_interval_minutes}분마다 | "
            f"식단: 매일 {settings.meal_send_hour}:{settings.meal_send_minute:02d}"
        )
        
        # 시작 알림
        await self.notifier.send_message(
            f"🚀 *영감봇 시작!*\n\n"
            f"💡 소프트웨어 아이디어: {settings.send_interval_minutes}분마다\n"
            f"🍽️ 토양체질 저녁 식단: 매일 {settings.meal_send_hour}:{settings.meal_send_minute:02d}\n\n"
            f"📅 시작 시각: {self.notifier.get_now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
    
    async def stop(self):
        """봇 종료"""
        self.scheduler.shutdown()
        await self.notifier.close()
        logger.info("⏹️ 영감봇 종료")
    
    async def send_daily_inspiration(self):
        """
        일일 영감 발송 (스케줄러에 의해 호출)
        """
        logger.info("💡 일일 영감 생성 중...")
        
        try:
            # 다음 발송할 아이디어 타입 결정 (히스토리 기반)
            next_type = self.generator.history.get_next_type()
            logger.info(f"💡 이번 발송 타입: {next_type}")
            
            idea = await self.generator.generate_idea(idea_type=next_type)
            result = await self.notifier.send_idea(idea)
            
            if result:
                logger.success(f"✅ 일일 영감 발송 완료! ({next_type})")
            else:
                logger.error("❌ 일일 영감 발송 실패")
                
        except Exception as e:
            logger.error(f"❌ 일일 영감 발송 에러: {e}")
    
    async def send_dinner_recommendation(self):
        """
        토양체질 저녁 식단 추천 발송 (매일 17:30 스케줄러)
        """
        logger.info("🍽️ 토양체질 저녁 식단 추천 생성 중...")
        
        try:
            menu = await self.meal_recommender.generate_dinner_menu()
            result = await self.notifier.send_idea(menu)
            
            if result:
                logger.success("✅ 저녁 식단 추천 발송 완료!")
            else:
                logger.error("❌ 저녁 식단 추천 발송 실패")
                
        except Exception as e:
            logger.error(f"❌ 저녁 식단 추천 발송 에러: {e}")
    
    async def send_test_inspiration(self):
        """
        테스트용 즉시 발송 (영감)
        """
        next_type = self.generator.history.get_next_type()
        logger.info(f"🧪 테스트 영감 생성 중... (타입: {next_type})")
        
        idea = await self.generator.generate_idea(idea_type=next_type)
        result = await self.notifier.send_idea(idea)
        return result

    async def send_test_meal(self):
        """
        테스트용 즉시 발송 (식단)
        """
        logger.info("🧪 테스트 식단 추천 생성 중...")
        
        menu = await self.meal_recommender.generate_dinner_menu()
        result = await self.notifier.send_idea(menu)
        return result


async def health_check(request):
    """Railway 헬스체크용"""
    return web.Response(text="OK", status=200)


async def main():
    """Entry point"""
    logger.info("=" * 40)
    logger.info("💡 Inspiration Bot v2.0.0")
    logger.info("   + 🍽️ 토양체질 식단 추천")
    logger.info("=" * 40)
    
    # 테스트 모드 체크
    test_mode = "--test" in sys.argv
    test_meal = "--test-meal" in sys.argv
    
    bot = InspirationBot()
    
    # HTTP 서버 (Railway 헬스체크용)
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)
    
    port = int(os.environ.get("PORT", settings.port))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"🌐 HTTP 서버 시작 (포트: {port})")
    
    await bot.start()
    
    # 테스트 모드: 아이디어 즉시 발송 후 종료
    if test_mode:
        logger.info("🧪 테스트 모드: 즉시 아이디어 발송")
        result = await bot.send_test_inspiration()
        print(f"\n테스트 결과: {'[OK] 성공' if result else '[FAIL] 실패'}")
        await bot.stop()
        return
    
    # 테스트 모드: 식단 즉시 발송 후 종료
    if test_meal:
        logger.info("🧪 테스트 모드: 즉시 식단 추천 발송")
        result = await bot.send_test_meal()
        print(f"\n테스트 결과: {'[OK] 성공' if result else '[FAIL] 실패'}")
        await bot.stop()
        return
    
    # 메인 루프
    try:
        while True:
            await asyncio.sleep(60)
    except asyncio.CancelledError:
        pass
    finally:
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
