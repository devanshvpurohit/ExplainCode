"""
Tests for practice challenge runner, progressive hints, and progression tracker.
"""

import os
import tempfile
import pytest
from explaincode.challenges import (
    CHALLENGES, ChallengeValidator, get_all_challenges, get_challenge_by_id
)
from explaincode.progression import ProgressionTracker, PROGRESSION_ORDER


def test_challenges_catalog():
    challenges = get_all_challenges()
    assert len(challenges) >= 6

    # Verify each challenge has required attributes
    for ch in challenges:
        assert ch.id
        assert ch.title
        assert ch.difficulty in ("Beginner", "Intermediate", "Advanced")
        assert ch.concept
        assert ch.problem_statement
        assert ch.starter_code
        assert len(ch.test_cases) >= 1
        assert len(ch.hints) >= 3


def test_challenge_validation_success():
    ch = get_challenge_by_id("ch_vars_01")
    assert ch is not None

    # Starter code passes the test case
    res = ChallengeValidator.validate_code(ch, ch.starter_code)
    assert res["passed"] is True
    assert len(res["test_results"]) == 1
    assert res["test_results"][0]["passed"] is True


def test_challenge_validation_failure():
    ch = get_challenge_by_id("ch_vars_01")
    assert ch is not None

    wrong_code = """ALGORITHM StoreMarks
INPUT:
OUTPUT: marks

STEP 1: Set marks == 42
STEP 2: RETURN marks

END ALGORITHM"""

    res = ChallengeValidator.validate_code(ch, wrong_code)
    assert res["passed"] is False
    assert res["test_results"][0]["passed"] is False
    assert "Expected return 85, got 42" in res["test_results"][0]["message"]


def test_progressive_hints():
    ch = get_challenge_by_id("ch_list_05")
    assert ch is not None
    assert len(ch.hints) == 3

    # Progressive reveal: Hint 1 is conceptual, Hint 3 is specific syntax
    assert "Hint 1" in ch.hints[0]
    assert "Hint 2" in ch.hints[1]
    assert "Hint 3" in ch.hints[2]


def test_progression_tracker_unlocks():
    with tempfile.TemporaryDirectory() as tmpdir:
        prog_path = os.path.join(tmpdir, "progress.json")
        tracker = ProgressionTracker(filepath=prog_path)

        # Initial state: only first concept unlocked
        assert tracker.is_concept_unlocked("Variables")
        assert not tracker.is_concept_unlocked("Input / Output")

        # Complete challenge in "Variables"
        tracker.complete_challenge("ch_vars_01", "Variables")
        assert tracker.is_challenge_completed("ch_vars_01")

        # Next concept should now be unlocked
        assert tracker.is_concept_unlocked("Input / Output")
        assert not tracker.is_concept_unlocked("Conditions")

        # Complete challenge in "Input / Output"
        tracker.complete_challenge("ch_io_02", "Input / Output")
        assert tracker.is_concept_unlocked("Conditions")

        # Check persistence by reloading from disk
        tracker2 = ProgressionTracker(filepath=prog_path)
        assert tracker2.is_concept_unlocked("Conditions")
        assert tracker2.is_challenge_completed("ch_vars_01")

        # Reset
        tracker.reset_progress()
        assert not tracker.is_concept_unlocked("Conditions")
        assert tracker.is_concept_unlocked("Variables")
