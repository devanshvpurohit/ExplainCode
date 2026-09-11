"""
Tests for 5-Level Python Transition Mode and Research Analytics.
"""

import os
import csv
import json
import tempfile
import pytest
from explaincode.transition import (
    TRANSITION_EXERCISES, TransitionManager, TransitionExercise
)
from explaincode.analytics import ResearchAnalytics


def test_transition_exercises_structure():
    exercises = TransitionManager.get_exercises()
    assert len(exercises) >= 5

    for ex in exercises:
        assert ex.id
        assert ex.title
        assert ex.concept
        assert ex.level1_description
        assert ex.level2_explaincode
        assert ex.level3_python
        assert ex.level4_scaffold
        assert len(ex.level4_expected_blanks) >= 1
        assert ex.level5_prompt
        assert len(ex.level5_test_cases) >= 1


def test_transition_level4_fill_blanks():
    ex = TransitionManager.get_exercise_by_id("tr_var_01")
    assert ex is not None

    # Correct fill
    ok, msg = TransitionManager.validate_level4(ex, ["10"])
    assert ok is True
    assert "Excellent" in msg

    # Wrong fill
    ok, msg = TransitionManager.validate_level4(ex, ["20"])
    assert ok is False
    assert "incorrect" in msg


def test_transition_level5_independent_python():
    ex = TransitionManager.get_exercise_by_id("tr_func_05")
    assert ex is not None

    correct_python = """
def Square(x):
    return x * x
"""
    ok, msg = TransitionManager.validate_level5(correct_python, ex.level5_test_cases)
    assert ok is True
    assert "All tests passed" in msg

    wrong_python = """
def Square(x):
    return x + 1
"""
    ok, msg = TransitionManager.validate_level5(wrong_python, ex.level5_test_cases)
    assert ok is False
    assert "failed" in msg


def test_research_analytics_logging_and_export():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "session_metrics.json")
        analytics = ResearchAnalytics(log_path=log_file, enabled=True)

        # Start an attempt
        analytics.start_challenge_attempt("ch_vars_01", "Variables", "Beginner")
        analytics.record_hint("ch_vars_01")
        analytics.record_error("ch_vars_01", "syntax")
        analytics.end_challenge_attempt("ch_vars_01", success=True)

        assert len(analytics.records) == 1
        rec = analytics.records[0]
        assert rec["challenge_id"] == "ch_vars_01"
        assert rec["hints_used"] == 1
        assert rec["errors_count"] == 1
        assert rec["success"] is True

        # Export CSV
        csv_path = os.path.join(tmpdir, "exported.csv")
        analytics.export_csv(csv_path)
        assert os.path.exists(csv_path)

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]["challenge_id"] == "ch_vars_01"
            assert rows[0]["success"] == "True"

        # Export JSON
        json_path = os.path.join(tmpdir, "exported.json")
        analytics.export_json(json_path)
        assert os.path.exists(json_path)
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert len(data) == 1
            assert data[0]["challenge_id"] == "ch_vars_01"
