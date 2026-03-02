"""
Inspiration Bot - Idea Summary Store
Stores concise summaries of generated ideas in a local text file.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, List

from loguru import logger

SUMMARY_FILE = "idea_summaries.txt"
SUMMARY_HEADER = (
    "# Inspiration Bot Idea Summaries\n"
    "# format: YYYY-MM-DD | type | title | summary\n"
)


class IdeaSummaryStore:
    """간략한 아이디어 요약을 파일로 관리"""

    def __init__(self):
        self.file_path = Path(__file__).parent / SUMMARY_FILE
        self._ensure_file()

    def _ensure_file(self):
        if self.file_path.exists():
            return
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(SUMMARY_HEADER)
            logger.info(f"🗂️ 아이디어 요약 파일 생성: {self.file_path.name}")
        except Exception as e:
            logger.error(f"요약 파일 생성 실패: {e}")

    def _parse_line(self, line: str) -> Dict[str, str]:
        parts = [p.strip() for p in line.split("|", 3)]
        if len(parts) != 4:
            return {}
        return {
            "date": parts[0],
            "type": parts[1],
            "title": parts[2],
            "summary": parts[3],
        }

    def get_entries(self) -> List[Dict[str, str]]:
        if not self.file_path.exists():
            return []

        entries: List[Dict[str, str]] = []
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    parsed = self._parse_line(line)
                    if parsed:
                        entries.append(parsed)
        except Exception as e:
            logger.error(f"요약 파일 읽기 실패: {e}")
        return entries

    def get_recent_context(self, limit: int = 60) -> str:
        """
        프롬프트 주입용 컨텍스트를 반환합니다.
        """
        entries = self.get_entries()
        if not entries:
            return ""

        recent = entries[-limit:]
        lines = [
            f"- {e['date']} | {e['type']} | {e['title']} | {e['summary']}"
            for e in recent
        ]
        return "\n".join(lines)

    def get_all_titles(self) -> List[str]:
        return [e["title"] for e in self.get_entries() if e.get("title")]

    def append_summary(self, title: str, idea_type: str, summary: str):
        safe_title = title.replace("\n", " ").replace("|", "/").strip()
        safe_summary = summary.replace("\n", " ").replace("|", "/").strip()
        line = (
            f"{datetime.now().strftime('%Y-%m-%d')} | "
            f"{idea_type} | {safe_title} | {safe_summary}\n"
        )
        try:
            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(line)
            logger.info(f"🗂️ 아이디어 요약 저장: {safe_title}")
        except Exception as e:
            logger.error(f"요약 파일 저장 실패: {e}")
