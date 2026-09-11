"""
explaincode.progression

Local progress and concept mastery tracking.
Unlocks the next concept as the learner solves challenges.
Stores state locally in ~/.explaincode/progress.json.
"""

import os
import json
from typing import List, Dict, Any, Set
from .challenges import CHALLENGES

PROGRESSION_ORDER = [
    "Variables",
    "Input / Output",
    "Conditions",
    "Loops",
    "Lists",
    "Functions",
    "Algorithms"
]

PROGRESS_DIR = os.path.expanduser("~/.explaincode")
PROGRESS_FILE = os.path.join(PROGRESS_DIR, "progress.json")


class ProgressionTracker:
    """Manages unlocked concepts and completed challenges."""

    def __init__(self, filepath: str = PROGRESS_FILE):
        self.filepath = filepath
        self.data: Dict[str, Any] = {
            "completed_challenges": [],
            "unlocked_concepts": [PROGRESSION_ORDER[0]],  # Start with first concept unlocked
            "hints_used": {}
        }
        self.load()

    def load(self):
        """Loads progression from disk if available."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self.data.update(saved)
            except Exception:
                pass
        # Ensure at least first concept is unlocked
        if PROGRESSION_ORDER[0] not in self.data.get("unlocked_concepts", []):
            self.data.setdefault("unlocked_concepts", []).append(PROGRESSION_ORDER[0])

    def save(self):
        """Persists progression data to local disk."""
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass

    def is_concept_unlocked(self, concept: str) -> bool:
        """Checks if a concept is currently unlocked."""
        return concept in self.data.get("unlocked_concepts", [])

    def is_challenge_completed(self, challenge_id: str) -> bool:
        """Checks if a challenge has been successfully completed."""
        return challenge_id in self.data.get("completed_challenges", [])

    def record_hint_used(self, challenge_id: str, hint_index: int):
        """Records that a hint was viewed for a challenge."""
        hints = self.data.setdefault("hints_used", {})
        curr = hints.get(challenge_id, 0)
        hints[challenge_id] = max(curr, hint_index + 1)
        self.save()

    def get_hints_used_count(self, challenge_id: str) -> int:
        return self.data.get("hints_used", {}).get(challenge_id, 0)

    def complete_challenge(self, challenge_id: str, concept: str):
        """Marks a challenge as completed and unlocks subsequent concepts."""
        completed: List[str] = self.data.setdefault("completed_challenges", [])
        if challenge_id not in completed:
            completed.append(challenge_id)

        # Check if we should unlock the next concept
        unlocked: List[str] = self.data.setdefault("unlocked_concepts", [])
        if concept in PROGRESSION_ORDER:
            idx = PROGRESSION_ORDER.index(concept)
            if idx + 1 < len(PROGRESSION_ORDER):
                next_concept = PROGRESSION_ORDER[idx + 1]
                if next_concept not in unlocked:
                    unlocked.append(next_concept)

        self.save()

    def get_status_overview(self) -> List[Dict[str, Any]]:
        """Returns ordered list of concepts with unlock and completion status."""
        result = []
        for concept in PROGRESSION_ORDER:
            concept_challenges = [c for c in CHALLENGES if c.concept == concept]
            all_done = bool(concept_challenges and all(self.is_challenge_completed(c.id) for c in concept_challenges))
            is_unlocked = self.is_concept_unlocked(concept)

            status = "locked"
            if is_unlocked:
                status = "completed" if all_done else "active"

            result.append({
                "concept": concept,
                "status": status,
                "is_unlocked": is_unlocked,
                "is_completed": all_done,
                "challenges_count": len(concept_challenges)
            })
        return result

    def reset_progress(self):
        """Resets progress back to level 1 initial state."""
        self.data = {
            "completed_challenges": [],
            "unlocked_concepts": [PROGRESSION_ORDER[0]],
            "hints_used": {}
        }
        self.save()
