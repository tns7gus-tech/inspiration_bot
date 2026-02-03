"""
Inspiration Bot - Configuration
Settings management using Pydantic
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """영감봇 설정"""
    
    # Telegram
    telegram_bot_token: str = Field(default="", description="Telegram Bot Token")
    telegram_chat_id: str = Field(default="", description="Telegram Chat ID")
    
    # Gemini AI
    gemini_api_key: str = Field(default="", description="Google Gemini API Key")
    gemini_model: str = Field(default="gemini-1.5-pro", description="Gemini 모델 (gemini-1.5-pro, gemini-1.5-flash, gemini-2.0-flash-exp)")
    
    # Schedule
    send_interval_minutes: int = Field(default=240, description="발송 간격 (분) - 4시간마다")
    send_hour: int = Field(default=9, description="발송 시간 (시) - interval 사용시 무시")
    send_minute: int = Field(default=0, description="발송 시간 (분) - interval 사용시 무시")
    timezone: str = Field(default="Asia/Seoul", description="타임존")
    
    # Server
    port: int = Field(default=8080, description="HTTP 포트")
    log_level: str = Field(default="INFO", description="로그 레벨")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
