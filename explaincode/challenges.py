"""
explaincode.challenges

Built-in challenge system with progressive exercises, test case evaluation,
and multi-tier progressive hints. No external database required.
"""

from typing import List, Dict, Any, Optional, Tuple
from .compiler import ExplainAIParser
from .stepper import ExplainCodeStepper


class Challenge:
    """Represents a structured coding challenge."""

    def __init__(
        self,
        id: str,
        title: str,
        difficulty: str,
        concept: str,
        problem_statement: str,
        starter_code: str,
        test_cases: List[Dict[str, Any]],
        hints: List[str]
    ):
        self.id = id
        self.title = title
        self.difficulty = difficulty
        self.concept = concept
        self.problem_statement = problem_statement
        self.starter_code = starter_code
        self.test_cases = test_cases
        self.hints = hints

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "difficulty": self.difficulty,
            "concept": self.concept,
            "problem_statement": self.problem_statement,
            "starter_code": self.starter_code,
            "hints_count": len(self.hints)
        }


# Graded challenge catalog
CHALLENGES: List[Challenge] = [
    Challenge(
        id="ch_vars_01",
        title="Student Marks Storage",
        difficulty="Beginner",
        concept="Variables",
        problem_statement="Create an algorithm that stores a student's marks (85) in a variable named 'marks' and displays them.",
        starter_code="""ALGORITHM StoreMarks
INPUT: 
OUTPUT: marks

STEP 1: Set marks ← 85
STEP 2: PRINT marks
STEP 3: RETURN marks

END ALGORITHM""",
        test_cases=[
            {
                "inputs": {},
                "expected_return": 85,
                "expected_outputs": ["85"]
            }
        ],
        hints=[
            "Hint 1: You need a variable to store the number 85.",
            "Hint 2: In ExplainCode, variables are assigned using 'Set name ← value'.",
            "Hint 3: Use 'STEP 1: Set marks ← 85' followed by 'STEP 2: PRINT marks' and 'RETURN marks'."
        ]
    ),
    Challenge(
        id="ch_io_02",
        title="Welcome Greeting",
        difficulty="Beginner",
        concept="Input / Output",
        problem_statement="Create an algorithm that accepts a person's name as input and displays a greeting 'Hello, ' followed by the name.",
        starter_code="""ALGORITHM GreetUser
INPUT: name
OUTPUT: greeting

STEP 1: Set greeting ← "Hello, " + name
STEP 2: PRINT greeting
STEP 3: RETURN greeting

END ALGORITHM""",
        test_cases=[
            {
                "inputs": {"name": "Alice"},
                "expected_return": "Hello, Alice",
                "expected_outputs": ["Hello, Alice"]
            },
            {
                "inputs": {"name": "Bob"},
                "expected_return": "Hello, Bob",
                "expected_outputs": ["Hello, Bob"]
            }
        ],
        hints=[
            "Hint 1: Notice the INPUT line specifies 'name'. You can use this variable directly.",
            "Hint 2: You can concatenate strings using the '+' operator.",
            "Hint 3: Use 'Set greeting ← \"Hello, \" + name' and 'PRINT greeting'."
        ]
    ),
    Challenge(
        id="ch_cond_03",
        title="Positive or Negative",
        difficulty="Beginner",
        concept="Conditions",
        problem_statement="Create an algorithm that takes a number 'num' and returns 'Positive' if num > 0, otherwise returns 'Negative or Zero'.",
        starter_code="""ALGORITHM CheckSign
INPUT: num
OUTPUT: result

STEP 1: IF num > 0 THEN
STEP 2:     Set result ← "Positive"
STEP 3: ELSE
STEP 4:     Set result ← "Negative or Zero"
STEP 5: END IF
STEP 6: RETURN result

END ALGORITHM""",
        test_cases=[
            {
                "inputs": {"num": 10},
                "expected_return": "Positive"
            },
            {
                "inputs": {"num": -5},
                "expected_return": "Negative or Zero"
            },
            {
                "inputs": {"num": 0},
                "expected_return": "Negative or Zero"
            }
        ],
        hints=[
            "Hint 1: You need an IF statement to make a decision based on the number.",
            "Hint 2: Use 'IF num > 0 THEN' to check for positive numbers.",
            "Hint 3: Use ELSE to handle numbers that are not greater than 0, and close with END IF."
        ]
    ),
    Challenge(
        id="ch_loop_04",
        title="Counting 1 to 10",
        difficulty="Beginner",
        concept="Loops",
        problem_statement="Create an algorithm that displays numbers from 1 to 10 using a FOR loop, and returns the final number 10.",
        starter_code="""ALGORITHM CountToTen
INPUT: 
OUTPUT: final_num

STEP 1: FOR i ← 1 to 10 DO
STEP 2:     PRINT i
STEP 3: END FOR
STEP 4: Set final_num ← 10
STEP 5: RETURN final_num

END ALGORITHM""",
        test_cases=[
            {
                "inputs": {},
                "expected_return": 10,
                "expected_outputs": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
            }
        ],
        hints=[
            "Hint 1: To repeat something 10 times, use a counting loop.",
            "Hint 2: ExplainCode supports 'FOR i ← 1 to 10 DO' ... 'END FOR'.",
            "Hint 3: Inside the loop, add 'PRINT i' to output each number."
        ]
    ),
    Challenge(
        id="ch_list_05",
        title="Find Largest Number in List",
        difficulty="Intermediate",
        concept="Lists",
        problem_statement="Given a non-empty list of numbers 'numbers', find and return the largest number.",
        starter_code="""ALGORITHM FindLargest
INPUT: numbers
OUTPUT: largest

STEP 1: Set largest ← numbers[0]
STEP 2: FOREACH num IN numbers DO
STEP 3:     IF num > largest THEN
STEP 4:         Set largest ← num
STEP 5:     END IF
STEP 6: END FOREACH
STEP 7: RETURN largest

END ALGORITHM""",
        test_cases=[
            {
                "inputs": {"numbers": [4, 9, 2, 15, 6]},
                "expected_return": 15
            },
            {
                "inputs": {"numbers": [100, 20, 50]},
                "expected_return": 100
            },
            {
                "inputs": {"numbers": [-10, -3, -25]},
                "expected_return": -3
            }
        ],
        hints=[
            "Hint 1: Start by assuming the first item 'numbers[0]' is currently the largest.",
            "Hint 2: Iterate through every element in 'numbers' with FOREACH.",
            "Hint 3: Compare each number: if num > largest, update largest ← num."
        ]
    ),
    Challenge(
        id="ch_func_06",
        title="Calculate Square of a Number",
        difficulty="Intermediate",
        concept="Functions",
        problem_statement="Create an algorithm that takes a number 'x' as input and returns its square (x * x).",
        starter_code="""ALGORITHM SquareNumber
INPUT: x
OUTPUT: squared

STEP 1: Set squared ← x * x
STEP 2: RETURN squared

END ALGORITHM""",
        test_cases=[
            {
                "inputs": {"x": 5},
                "expected_return": 25
            },
            {
                "inputs": {"x": 12},
                "expected_return": 144
            },
            {
                "inputs": {"x": -4},
                "expected_return": 16
            }
        ],
        hints=[
            "Hint 1: The square of a number is simply the number multiplied by itself.",
            "Hint 2: In ExplainCode, multiply using '*', such as x * x.",
            "Hint 3: Assign the product to a variable and RETURN it."
        ]
    ),
    Challenge(
        id="ch_algo_07",
        title="Sum Numbers Until Limit",
        difficulty="Advanced",
        concept="Algorithms",
        problem_statement="Given a list 'numbers' and a 'limit', iterate through 'numbers' adding each to a running total. If the total exceeds 'limit', stop immediately using BREAK and return the total.",
        starter_code="""ALGORITHM SumUntilLimit
INPUT: numbers, limit
OUTPUT: total

STEP 1: Set total ← 0
STEP 2: FOREACH num IN numbers DO
STEP 3:     Set total ← total + num
STEP 4:     IF total > limit THEN
STEP 5:         BREAK
STEP 6:     END IF
STEP 7: END FOREACH
STEP 8: RETURN total

END ALGORITHM""",
        test_cases=[
            {
                "inputs": {"numbers": [10, 20, 30, 40, 50], "limit": 55},
                "expected_return": 60
            },
            {
                "inputs": {"numbers": [5, 5, 5], "limit": 100},
                "expected_return": 15
            }
        ],
        hints=[
            "Hint 1: Keep a variable 'total' initialized to 0.",
            "Hint 2: Add each number to 'total' inside a loop.",
            "Hint 3: Use 'IF total > limit THEN BREAK END IF' to exit early."
        ]
    )
]


class ChallengeValidator:
    """Validates ExplainCode solutions against test cases."""

    @staticmethod
    def validate_code(challenge: Challenge, code_text: str) -> Dict[str, Any]:
        """
        Parses and runs learner's ExplainCode against each test case in the challenge.
        Returns validation results with pass/fail summary.
        """
        lines = code_text.splitlines()
        parser = ExplainAIParser()

        try:
            ast_tree = parser.parse(lines)
        except Exception as e:
            return {
                "passed": False,
                "error": f"Syntax Error: {str(e)}",
                "test_results": []
            }

        test_results = []
        all_passed = True

        for idx, tc in enumerate(challenge.test_cases, 1):
            inputs = tc.get("inputs", {})
            expected_ret = tc.get("expected_return")
            expected_outs = tc.get("expected_outputs")

            stepper = ExplainCodeStepper(ast_tree, initial_inputs=inputs)
            stepper.run_all()

            actual_ret = stepper.return_value
            actual_outs = stepper.output_log

            passed_case = True
            msg = ""

            if stepper.error:
                passed_case = False
                msg = f"Runtime error: {stepper.error}"
            elif expected_ret is not None and actual_ret != expected_ret:
                passed_case = False
                msg = f"Expected return {expected_ret!r}, got {actual_ret!r}"
            elif expected_outs is not None:
                if actual_outs != expected_outs:
                    passed_case = False
                    msg = f"Expected outputs {expected_outs!r}, got {actual_outs!r}"

            if not passed_case:
                all_passed = False

            test_results.append({
                "test_case": idx,
                "inputs": inputs,
                "passed": passed_case,
                "expected_return": expected_ret,
                "actual_return": actual_ret,
                "message": msg or "Passed"
            })

        return {
            "passed": all_passed,
            "test_results": test_results,
            "challenge_id": challenge.id,
            "concept": challenge.concept
        }


def get_all_challenges() -> List[Challenge]:
    return CHALLENGES


def get_challenge_by_id(cid: str) -> Optional[Challenge]:
    for ch in CHALLENGES:
        if ch.id == cid:
            return ch
    return None
