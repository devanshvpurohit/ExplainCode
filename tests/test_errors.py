"""
Tests for pedagogical error diagnosis (Beginner Explanation + Technical Error).
"""

import pytest
from explaincode.errors import ErrorTutor, ErrorReport


def test_syntax_missing_end_if():
    code = [
        "ALGORITHM MissingEndIf",
        "INPUT: score",
        "STEP 1: IF score > 50 THEN",
        "STEP 2:     DISPLAY \"Pass\"",
        "END ALGORITHM"
    ]
    report = ErrorTutor.diagnose_syntax(code)
    assert report is not None
    assert "The algorithm is missing END IF" in report.problem
    assert "Every IF block must eventually be closed" in report.concept
    assert "IF condition THEN" in report.expected
    assert "Add END IF" in report.suggestion
    assert "SyntaxError" in report.technical_error

    formatted = report.to_formatted_string()
    assert "Problem:" in formatted
    assert "Concept:" in formatted
    assert "Expected Pattern:" in formatted
    assert "Suggestion:" in formatted
    assert "Technical Error:" in formatted


def test_syntax_missing_then():
    code = [
        "ALGORITHM MissingThen",
        "INPUT: x",
        "STEP 1: IF x > 0",
        "STEP 2:     DISPLAY \"Positive\"",
        "STEP 3: END IF",
        "END ALGORITHM"
    ]
    report = ErrorTutor.diagnose_syntax(code)
    assert report is not None
    assert "missing THEN" in report.problem
    assert "SyntaxError" in report.technical_error


def test_syntax_missing_assignment_arrow():
    code = [
        "ALGORITHM BadAssign",
        "INPUT:",
        "STEP 1: SET count = 10",
        "END ALGORITHM"
    ]
    report = ErrorTutor.diagnose_syntax(code)
    assert report is not None
    assert "missing the arrow operator '←'" in report.problem
    assert "Replace '=' with the arrow operator '←'" in report.suggestion


def test_syntax_missing_loop_terminator():
    code = [
        "ALGORITHM UnclosedLoop",
        "INPUT:",
        "STEP 1: FOR i ← 1 to 5 DO",
        "STEP 2:     PRINT i",
        "END ALGORITHM"
    ]
    report = ErrorTutor.diagnose_syntax(code)
    assert report is not None
    assert "missing END FOR" in report.problem


def test_runtime_name_error():
    exc = NameError("name 'foo' is not defined")
    report = ErrorTutor.diagnose_runtime(exc, current_statement="PRINT foo")
    assert "Variable 'foo' was used before it was given a value" in report.problem
    assert "Variables must be created or defined with SET or INPUT" in report.concept
    assert "NameError" in report.technical_error
    assert "PRINT foo" in report.to_formatted_string()


def test_runtime_zero_division():
    exc = ZeroDivisionError("division by zero")
    report = ErrorTutor.diagnose_runtime(exc, current_statement="Set res ← a / b")
    assert "Attempted to divide a number by zero" in report.problem
    assert "ZeroDivisionError" in report.technical_error


def test_runtime_index_error():
    exc = IndexError("list index out of range")
    report = ErrorTutor.diagnose_runtime(exc)
    assert "Tried to access an item at an index that does not exist" in report.problem
    assert "IndexError" in report.technical_error


def test_runtime_key_error():
    exc = KeyError("missing_key")
    report = ErrorTutor.diagnose_runtime(exc)
    assert "missing_key" in report.problem
    assert "KeyError" in report.technical_error
