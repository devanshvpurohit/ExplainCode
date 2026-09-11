"""
explaincode.transition

Python Transition Mode: A 5-level scaffolding progression guiding learners
from Natural-Language algorithmic thinking to writing independent Python code.

Level 1: Natural-Language Thinking (logic & pseudocode understanding)
Level 2: ExplainCode (formal natural-language programming)
Level 3: Side-by-Side Dual View (ExplainCode + Python Equivalent)
Level 4: Fill-in-the-Blank Python (completing missing Python tokens/expressions)
Level 5: Write Python Independently (writing pure Python tested against specifications)
"""

import ast
from typing import Dict, Any, List, Optional, Tuple


class TransitionExercise:
    """A multi-level transition exercise."""

    def __init__(
        self,
        id: str,
        title: str,
        concept: str,
        level1_description: str,
        level2_explaincode: str,
        level3_python: str,
        level4_scaffold: str,
        level4_expected_blanks: List[str],
        level5_prompt: str,
        level5_test_cases: List[Dict[str, Any]]
    ):
        self.id = id
        self.title = title
        self.concept = concept
        self.level1_description = level1_description
        self.level2_explaincode = level2_explaincode
        self.level3_python = level3_python
        self.level4_scaffold = level4_scaffold
        self.level4_expected_blanks = level4_expected_blanks
        self.level5_prompt = level5_prompt
        self.level5_test_cases = level5_test_cases

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "concept": self.concept,
            "level1_description": self.level1_description,
            "level2_explaincode": self.level2_explaincode,
            "level3_python": self.level3_python,
            "level4_scaffold": self.level4_scaffold,
            "level5_prompt": self.level5_prompt
        }


TRANSITION_EXERCISES: List[TransitionExercise] = [
    TransitionExercise(
        id="tr_var_01",
        title="Variable Assignment",
        concept="Variables",
        level1_description="Goal: Store the number 10 in a variable called 'x'. In plain English: 'Create a box named x and put 10 inside it.'",
        level2_explaincode="""ALGORITHM StoreValue
INPUT:
OUTPUT: x

STEP 1: Set x ← 10
STEP 2: RETURN x

END ALGORITHM""",
        level3_python="""def StoreValue():
    x = 10
    return x""",
        level4_scaffold="""def StoreValue():
    x = ______
    return x""",
        level4_expected_blanks=["10"],
        level5_prompt="Write a Python function `StoreValue()` that creates variable `x` with value 10 and returns `x`.",
        level5_test_cases=[
            {"call": "StoreValue()", "expected": 10}
        ]
    ),
    TransitionExercise(
        id="tr_cond_02",
        title="Conditional Statement",
        concept="Conditions",
        level1_description="Goal: Given a number x, if x is greater than 5, print x. In plain English: 'Check if x is bigger than 5. If it is, output it.'",
        level2_explaincode="""ALGORITHM CheckThreshold
INPUT: x
OUTPUT: None

STEP 1: IF x > 5 THEN
STEP 2:     PRINT x
STEP 3: END IF

END ALGORITHM""",
        level3_python="""def CheckThreshold(x):
    if x > 5:
        print(x)""",
        level4_scaffold="""def CheckThreshold(x):
    if x > ______:
        print(______)""",
        level4_expected_blanks=["5", "x"],
        level5_prompt="Write a Python function `CheckThreshold(x)` that checks if x > 5 and returns True if x > 5 else False.",
        level5_test_cases=[
            {"call": "CheckThreshold(10)", "expected": True},
            {"call": "CheckThreshold(3)", "expected": False}
        ]
    ),
    TransitionExercise(
        id="tr_loop_03",
        title="Loop Counting",
        concept="Loops",
        level1_description="Goal: Sum numbers from 1 to 5. In plain English: 'Start with sum at 0. For each number from 1 to 5, add it to sum. Finally return sum.'",
        level2_explaincode="""ALGORITHM SumUpToFive
INPUT:
OUTPUT: total

STEP 1: Set total ← 0
STEP 2: FOR i ← 1 to 5 DO
STEP 3:     Set total ← total + i
STEP 4: END FOR
STEP 5: RETURN total

END ALGORITHM""",
        level3_python="""def SumUpToFive():
    total = 0
    for i in range(1, 6):
        total = total + i
    return total""",
        level4_scaffold="""def SumUpToFive():
    total = 0
    for i in range(1, ______):
        total = total + ______
    return total""",
        level4_expected_blanks=["6", "i"],
        level5_prompt="Write a Python function `SumUpToFive()` that calculates and returns the sum of integers from 1 through 5 using a loop.",
        level5_test_cases=[
            {"call": "SumUpToFive()", "expected": 15}
        ]
    ),
    TransitionExercise(
        id="tr_list_04",
        title="List Traversal",
        concept="Lists",
        level1_description="Goal: Double each number in a list of numbers. In plain English: 'For every number in our collection, multiply it by 2 and put it in a new list.'",
        level2_explaincode="""ALGORITHM DoubleList
INPUT: numbers
OUTPUT: doubled

STEP 1: MAP numbers WITH x * 2 → doubled
STEP 2: RETURN doubled

END ALGORITHM""",
        level3_python="""def DoubleList(numbers):
    doubled = [_x * 2 for _x in numbers]
    return doubled""",
        level4_scaffold="""def DoubleList(numbers):
    doubled = [x * 2 for x in ______]
    return doubled""",
        level4_expected_blanks=["numbers"],
        level5_prompt="Write a Python function `DoubleList(numbers)` that returns a new list containing each number multiplied by 2.",
        level5_test_cases=[
            {"call": "DoubleList([1, 2, 3])", "expected": [2, 4, 6]},
            {"call": "DoubleList([])", "expected": []}
        ]
    ),
    TransitionExercise(
        id="tr_func_05",
        title="Square Function",
        concept="Functions",
        level1_description="Goal: Define a reusable function that calculates the square of a number. In plain English: 'Take an input x and multiply x by itself.'",
        level2_explaincode="""ALGORITHM Square
INPUT: x
OUTPUT: result

STEP 1: Set result ← x * x
STEP 2: RETURN result

END ALGORITHM""",
        level3_python="""def Square(x):
    result = x * x
    return result""",
        level4_scaffold="""def Square(x):
    result = ______ * ______
    return result""",
        level4_expected_blanks=["x", "x"],
        level5_prompt="Write a Python function `Square(x)` that returns the square of x.",
        level5_test_cases=[
            {"call": "Square(4)", "expected": 16},
            {"call": "Square(-3)", "expected": 9}
        ]
    )
]


class TransitionManager:
    """Manages exercises and validates Level 4 (fill-in-the-blank) and Level 5 (independent Python)."""

    @staticmethod
    def get_exercises() -> List[TransitionExercise]:
        return TRANSITION_EXERCISES

    @staticmethod
    def get_exercise_by_id(eid: str) -> Optional[TransitionExercise]:
        for ex in TRANSITION_EXERCISES:
            if ex.id == eid:
                return ex
        return None

    @staticmethod
    def validate_level4(exercise: TransitionExercise, user_answers: List[str]) -> Tuple[bool, str]:
        """Validates filled blanks against expected answers."""
        cleaned_user = [a.strip() for a in user_answers]
        expected = [e.strip() for e in exercise.level4_expected_blanks]

        if len(cleaned_user) != len(expected):
            return False, f"Expected {len(expected)} blank(s), but received {len(cleaned_user)}."

        for i, (user_ans, exp_ans) in enumerate(zip(cleaned_user, expected)):
            if user_ans != exp_ans:
                return False, f"Blank #{i+1} is incorrect. You provided '{user_ans}', but expected '{exp_ans}'."

        return True, "🎉 Excellent! All blanks filled correctly."

    @staticmethod
    def validate_level5(user_python_code: str, test_cases: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """Executes learner's independent Python code in an isolated scope and tests cases."""
        local_scope: Dict[str, Any] = {}
        try:
            exec(user_python_code, {}, local_scope)
        except Exception as e:
            return False, f"Syntax or execution error in Python code: {str(e)}"

        for idx, tc in enumerate(test_cases, 1):
            call_expr = tc.get("call")
            expected_val = tc.get("expected")
            try:
                actual_val = eval(call_expr, {}, local_scope)
            except Exception as e:
                return False, f"Test {idx} ({call_expr}) raised error: {str(e)}"

            if actual_val != expected_val:
                return False, f"Test {idx} failed: {call_expr} returned {actual_val!r}, expected {expected_val!r}."

        return True, "🎉 All tests passed! You have successfully transitioned to writing independent Python code."
