"""
Inspiration Bot - Meal History Manager
Tracks recommended meals to prevent duplicates across days
"""
import json
from datetime import datetime
from pathlib import Path
from typing import List
from loguru import logger

MEAL_HISTORY_FILE = "meal_history.json"


class MealHistory:
    """식단 추천 히스토리 관리 (중복 방지)"""

    def __init__(self):
        self.file_path = Path(__file__).parent / MEAL_HISTORY_FILE
        self.data = self._load_data()

    def _load_data(self) -> dict:
        """Load history from JSON file"""
        if not self.file_path.exists():
            return {"history": []}

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load meal history: {e}")
            return {"history": []}

    def _save_data(self):
        """Save history to JSON file"""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save meal history: {e}")

    def record_meals(self, meal_titles: List[str]):
        """
        추천된 메뉴 제목들을 기록합니다.

        Args:
            meal_titles: 추천된 메뉴 이름 리스트
        """
        if "history" not in self.data:
            self.data["history"] = []

        entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "meals": meal_titles
        }
        self.data["history"].append(entry)

        # 최근 90일치만 유지 (약 3개월)
        if len(self.data["history"]) > 90:
            self.data["history"] = self.data["history"][-90:]

        self._save_data()
        logger.info(f"🍽️ {len(meal_titles)}개 메뉴 히스토리 저장 완료")

    def get_recent_meals(self, days: int = 30) -> List[str]:
        """
        최근 N일치 추천 메뉴 제목 목록 반환 (중복 방지용)

        Args:
            days: 조회할 일수 (기본 30일)

        Returns:
            메뉴 제목 리스트
        """
        history = self.data.get("history", [])
        recent = history[-days:] if len(history) > days else history

        titles = []
        for entry in recent:
            titles.extend(entry.get("meals", []))

        return titles

    def get_today_meals(self) -> List[str]:
        """오늘 이미 추천된 메뉴 목록 반환"""
        today = datetime.now().strftime("%Y-%m-%d")
        history = self.data.get("history", [])

        for entry in history:
            if entry.get("date") == today:
                return entry.get("meals", [])

        return []
