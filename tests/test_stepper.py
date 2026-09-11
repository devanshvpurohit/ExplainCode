"""
Tests for step-by-step execution, variable tracking, conditionals, loops, and reset.
"""

import pytest
from explaincode.compiler import ExplainCodeParser
from explaincode.stepper import ExplainCodeStepper


def test_step_execution_and_variable_tracking():
    code = [
        "ALGORITHM StepVars",
        "INPUT:",
        "STEP 1: Set a == 10",
        "STEP 2: Set b == 20",
        "STEP 3: Set sum == a + b",
        "STEP 4: RETURN sum",
        "END ALGORITHM"
    ]
    parser = ExplainCodeParser()
    ast_tree = parser.parse(code)
    stepper = ExplainCodeStepper(ast_tree)

    # Step 1
    s1 = stepper.step()
    assert s1.env["a"] == 10
    assert s1.changed_vars == {"a": 10}
    assert not stepper.is_done()

    # Step 2
    s2 = stepper.step()
    assert s2.env["b"] == 20
    assert s2.changed_vars == {"b": 20}

    # Step 3
    s3 = stepper.step()
    assert s3.env["sum"] == 30
    assert s3.changed_vars == {"sum": 30}

    # Step 4 (Return)
    s4 = stepper.step()
    assert s4.return_value == 30
    assert s4.is_finished
    assert stepper.is_done()


def test_if_execution_branching():
    code = [
        "ALGORITHM BranchTest",
        "INPUT: x",
        "STEP 1: IF x > 5 THEN",
        "STEP 2:     Set status == \"high\"",
        "STEP 3: ELSE",
        "STEP 4:     Set status == \"low\"",
        "STEP 5: END IF",
        "STEP 6: RETURN status",
        "END ALGORITHM"
    ]
    parser = ExplainCodeParser()
    ast_tree = parser.parse(code)

    # Case 1: x = 10 -> high
    stepper1 = ExplainCodeStepper(ast_tree, initial_inputs={"x": 10})
    s1 = stepper1.step()  # IF x > 5
    assert s1.condition_info["result"] is True
    assert "THEN" in s1.condition_info["branch_taken"]
    stepper1.run_all()
    assert stepper1.return_value == "high"

    # Case 2: x = 2 -> low
    stepper2 = ExplainCodeStepper(ast_tree, initial_inputs={"x": 2})
    s1 = stepper2.step()  # IF x > 5
    assert s1.condition_info["result"] is False
    stepper2.run_all()
    assert stepper2.return_value == "low"


def test_for_execution_iteration():
    code = [
        "ALGORITHM ForTest",
        "INPUT:",
        "STEP 1: Set total == 0",
        "STEP 2: FOR i == 1 to 3 DO",
        "STEP 3:     Set total == total + i",
        "STEP 4: END FOR",
        "STEP 5: RETURN total",
        "END ALGORITHM"
    ]
    parser = ExplainCodeParser()
    ast_tree = parser.parse(code)
    stepper = ExplainCodeStepper(ast_tree)

    states = stepper.run_all()
    assert stepper.return_value == 6
    assert stepper.env["total"] == 6


def test_foreach_and_break_execution():
    code = [
        "ALGORITHM ForeachBreak",
        "INPUT:",
        "STEP 1: LIST nums == [2, 4, 9, 8]",
        "STEP 2: Set found_odd == 0",
        "STEP 3: FOREACH n IN nums DO",
        "STEP 4:     IF n % 2 != 0 THEN",
        "STEP 5:         Set found_odd == n",
        "STEP 6:         BREAK",
        "STEP 7:     END IF",
        "STEP 8: END FOREACH",
        "STEP 9: RETURN found_odd",
        "END ALGORITHM"
    ]
    parser = ExplainCodeParser()
    ast_tree = parser.parse(code)
    stepper = ExplainCodeStepper(ast_tree)
    stepper.run_all()

    assert stepper.return_value == 9


def test_while_execution():
    code = [
        "ALGORITHM WhileTest",
        "INPUT: n",
        "STEP 1: Set count == 0",
        "STEP 2: WHILE n > 0 DO",
        "STEP 3:     Set count == count + 1",
        "STEP 4:     Set n == n - 1",
        "STEP 5: END WHILE",
        "STEP 6: RETURN count",
        "END ALGORITHM"
    ]
    parser = ExplainCodeParser()
    ast_tree = parser.parse(code)
    stepper = ExplainCodeStepper(ast_tree, initial_inputs={"n": 4})
    stepper.run_all()

    assert stepper.return_value == 4
    assert stepper.env["n"] == 0


def test_reset_functionality():
    code = [
        "ALGORITHM ResetTest",
        "INPUT: start",
        "STEP 1: Set count == start",
        "STEP 2: Set count == count + 10",
        "STEP 3: RETURN count",
        "END ALGORITHM"
    ]
    parser = ExplainCodeParser()
    ast_tree = parser.parse(code)
    stepper = ExplainCodeStepper(ast_tree, initial_inputs={"start": 5})

    # Run two steps
    stepper.step()
    stepper.step()
    assert stepper.env["count"] == 15

    # Reset
    stepper.reset()
    assert stepper.pc == 0
    assert stepper.env.get("count") is None
    assert stepper.is_done() is False
    assert stepper.return_value is None

    # Step again from beginning
    stepper.step()
    assert stepper.env["count"] == 5
