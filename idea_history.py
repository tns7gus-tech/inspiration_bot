"""
Inspiration Bot - Idea History Manager
Manages duplicate checks and alternates between idea types
"""
import json
import os
from pathlib import Path
from typing import List, Optional
from loguru import logger

HISTORY_FILE = "idea_history.json"

class IdeaHistory:
    def __init__(self):
        self.file_path = Path(__file__).parent / HISTORY_FILE
        self.data = self._load_data()
    
    def _load_data(self) -> dict:
        """Load history from JSON file"""
        if not self.file_path.exists():
            return {
                "last_type": "software",  # Start with hardware (next will be mixed -> actually let's toggle) 
                # If last was software, next is mixed (hardware+sw). If last was mixed, next is software.
                # Let's set default last_type to 'software' so the very first one is 'mixed' (Hardware+SW) as per user habit?
                # Or 'mixed' so first is 'software'? User wants new SW ideas. Let's start with mixed so next is software?
                # Actually user complained about current hardware ideas. Let's make the NEXT one Software.
                # So set last_type = 'mixed'.
                "history": []
            }
        
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load history: {e}")
            return {"last_type": "mixed", "history": []}
    
    def _save_data(self):
        """Save history to JSON file"""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save history: {e}")

    def get_next_type(self) -> str:
        """Get the next idea type to generate (software only)"""
        # 소프트웨어 아이디어만 발송 (하드웨어/mixed 제외)
        return "software"

    def record_idea(self, title: str, idea_type: str):
        """Record a new idea and update last type"""
        self.data["last_type"] = idea_type
        
        # Add to history
        if "history" not in self.data:
            self.data["history"] = []
            
        self.data["history"].append({
            "title": title,
            "type": idea_type
        })
        
        # Keep only last 100 items
        if len(self.data["history"]) > 100:
            self.data["history"] = self.data["history"][-100:]
            
        self._save_data()

    def is_duplicate(self, title: str) -> bool:
        """Check if idea title already exists"""
        for item in self.data.get("history", []):
            if item.get("title") == title:
                return True
        return False
    
    def get_recent_titles(self, limit: int = 20) -> List[str]:
        """Get list of recent titles to include in prompt"""
        history = self.data.get("history", [])
        return [item["title"] for item in history[-limit:]]
