"""
explaincode.analytics

Lightweight, strictly anonymous educational research data collection.
Records learning metrics locally to enable evaluation of learning gains,
syntax error trends, hint dependency, and Python transition efficacy.
Zero personally identifiable information (PII) is collected.
"""

import os
import csv
import json
import time
import uuid
from typing import Dict, Any, List, Optional

ANALYTICS_DIR = os.path.expanduser("~/.explaincode/research")
LOG_FILE = os.path.join(ANALYTICS_DIR, "session_metrics.json")


class ResearchAnalytics:
    """Logs and exports anonymous learning session metrics."""

    def __init__(self, log_path: str = LOG_FILE, enabled: bool = False):
        self.log_path = log_path
        self.enabled = enabled
        self.session_id = str(uuid.uuid4())[:8]
        self.records: List[Dict[str, Any]] = []
        self._active_attempts: Dict[str, Dict[str, Any]] = {}
        self.load()

    def set_enabled(self, enabled: bool):
        self.enabled = enabled

    def load(self):
        if os.path.exists(self.log_path):
            try:
                with open(self.log_path, "r", encoding="utf-8") as f:
                    self.records = json.load(f)
            except Exception:
                self.records = []

    def start_challenge_attempt(self, challenge_id: str, concept: str, difficulty: str):
        """Starts timing and tracking an attempt for a challenge."""
        if not self.enabled:
            return
        self._active_attempts[challenge_id] = {
            "session_id": self.session_id,
            "challenge_id": challenge_id,
            "concept": concept,
            "difficulty": difficulty,
            "start_time": time.time(),
            "hints_used": 0,
            "errors_count": 0,
            "attempts_count": self._active_attempts.get(challenge_id, {}).get("attempts_count", 0) + 1
        }

    def record_hint(self, challenge_id: str):
        if not self.enabled:
            return
        if challenge_id in self._active_attempts:
            self._active_attempts[challenge_id]["hints_used"] += 1

    def record_error(self, challenge_id: str, error_kind: str = "syntax"):
        if not self.enabled:
            return
        if challenge_id in self._active_attempts:
            self._active_attempts[challenge_id]["errors_count"] += 1

    def end_challenge_attempt(self, challenge_id: str, success: bool):
        """Records outcome and calculates duration."""
        if not self.enabled or challenge_id not in self._active_attempts:
            return

        att = self._active_attempts[challenge_id]
        duration = round(time.time() - att["start_time"], 2)

        record = {
            "session_id": att["session_id"],
            "challenge_id": challenge_id,
            "concept": att["concept"],
            "difficulty": att["difficulty"],
            "attempts": att["attempts_count"],
            "success": success,
            "completion_time_sec": duration,
            "hints_used": att["hints_used"],
            "errors_count": att["errors_count"],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        self.records.append(record)
        self._save()

    def _save(self):
        try:
            os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
            with open(self.log_path, "w", encoding="utf-8") as f:
                json.dump(self.records, f, indent=2)
        except Exception:
            pass

    def export_json(self, output_path: str) -> str:
        """Exports all recorded metrics to a JSON file."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.records, f, indent=2)
        return output_path

    def export_csv(self, output_path: str) -> str:
        """Exports all recorded metrics to a CSV file for research analysis."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        fieldnames = [
            "session_id", "challenge_id", "concept", "difficulty",
            "attempts", "success", "completion_time_sec", "hints_used",
            "errors_count", "timestamp"
        ]
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in self.records:
                writer.writerow(r)
        return output_path

    def clear_metrics(self):
        self.records.clear()
        self._save()
