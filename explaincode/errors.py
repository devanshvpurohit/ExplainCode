"""
explaincode.errors

Pedagogical error diagnostic layer for ExplainCode.
Translates syntax errors and runtime exceptions into actionable, dual-layer feedback:
1. Beginner Explanation (Problem, Concept, Expected pattern, Actionable suggestion)
2. Technical Error (original exception type and details)
"""

import re
from typing import Dict, Any, Optional, List, Tuple


class ErrorReport:
    """Holds both learner-friendly explanation and raw technical error."""

    def __init__(
        self,
        problem: str,
        concept: str,
        expected: str,
        suggestion: str,
        technical_error: str,
        line_number: Optional[int] = None,
        source_line: Optional[str] = None
    ):
        self.problem = problem
        self.concept = concept
        self.expected = expected
        self.suggestion = suggestion
        self.technical_error = technical_error
        self.line_number = line_number
        self.source_line = source_line

    def to_formatted_string(self, include_concept: bool = False) -> str:
        loc = f" (Line {self.line_number})" if self.line_number else ""
        lines = [
            f"❌ Something went wrong{loc}\n",
            f"Problem:\n  {self.problem}\n",
        ]
        if self.source_line:
            lines.append(f"Line content:\n  >>> {self.source_line}\n")
        if include_concept and self.concept:
            lines.append(f"Concept:\n  {self.concept}\n")
        lines.extend([
            f"Expected Pattern:\n{self.expected}\n",
            f"Suggestion:\n  {self.suggestion}\n",
            "--------------------------------------------------",
            f"Technical Error:\n  {self.technical_error}"
        ])
        return "\n".join(lines)


class ErrorTutor:
    """Diagnoses ExplainCode errors during parsing and execution."""

    @staticmethod
    def diagnose_syntax(code_lines: List[str]) -> Optional[ErrorReport]:
        """Scans raw lines for common beginner syntax mistakes before or during parse."""
        cleaned = [l.strip() for l in code_lines if l.strip() and not l.strip().startswith("#")]
        if not cleaned:
            return ErrorReport(
                problem="The code file is empty.",
                concept="Every ExplainCode file requires an algorithm definition.",
                expected="ALGORITHM MyAlgorithm\nINPUT: ...\nSTEP 1: ...\nEND ALGORITHM",
                suggestion="Add an ALGORITHM header, at least one STEP, and an END ALGORITHM line.",
                technical_error="SyntaxError: Empty program"
            )

        # 1. Header check
        if not cleaned[0].startswith(("ALGORITHM", "MODEL", "API_CALL")):
            return ErrorReport(
                problem="The algorithm is missing a starting header.",
                concept="ExplainCode programs must begin with ALGORITHM or MODEL followed by a name.",
                expected="ALGORITHM CalculateTotal",
                suggestion=f"Start line 1 with 'ALGORITHM Name' instead of '{cleaned[0][:30]}'.",
                technical_error="SyntaxError: File must start with ALGORITHM, MODEL, or API_CALL.",
                line_number=1,
                source_line=cleaned[0]
            )

        # 2. Tail check
        if not any(l.startswith(("END ALGORITHM", "END MODEL", "END API_CALL")) for l in cleaned):
            return ErrorReport(
                problem="The algorithm is missing an closing terminator.",
                concept="Every ALGORITHM or MODEL block must eventually be closed.",
                expected="...\nEND ALGORITHM",
                suggestion="Add 'END ALGORITHM' at the very end of your code.",
                technical_error="SyntaxError: Expected 'END ALGORITHM' at end of file.",
                line_number=len(code_lines)
            )

        # 3. Block matching (IF / END IF, FOR / END FOR, etc.)
        if_stack: List[int] = []
        for_stack: List[int] = []
        while_stack: List[int] = []
        try_stack: List[int] = []

        for idx, line in enumerate(code_lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            # Strip STEP N: prefix if present for statement classification
            content = re.sub(r"^STEP\s+\d+:?\s*", "", stripped).strip()

            # Check assignment arrow
            if re.search(r"^(?:Set|SET)\b", content) and "←" not in content:
                return ErrorReport(
                    problem="The assignment is missing the arrow operator '←'.",
                    concept="ExplainCode uses the left arrow '←' to assign values to variables.",
                    expected="SET variable_name ← value",
                    suggestion="Replace '=' with the arrow operator '←' (e.g. SET total ← 0).",
                    technical_error="SyntaxError: Missing assignment operator '←'",
                    line_number=idx,
                    source_line=line
                )

            # Block: END IF
            if content.startswith("END IF"):
                if if_stack:
                    if_stack.pop()
                else:
                    return ErrorReport(
                        problem="Found an extra 'END IF' without a matching 'IF'.",
                        concept="END IF closes an earlier IF statement, but no open IF was found.",
                        expected="IF condition THEN\n    ...\nEND IF",
                        suggestion="Remove this redundant 'END IF' or check earlier IF lines.",
                        technical_error="SyntaxError: Unmatched 'END IF'",
                        line_number=idx,
                        source_line=line
                    )
            # Block: IF ... THEN
            elif content.startswith("IF ") or content == "IF":
                if "THEN" not in content:
                    return ErrorReport(
                        problem="The IF statement is missing THEN.",
                        concept="Every IF statement condition must be followed by THEN before statements.",
                        expected="IF condition THEN\n    ...\nEND IF",
                        suggestion="Add 'THEN' after your condition on this line.",
                        technical_error="SyntaxError: Missing THEN in IF statement",
                        line_number=idx,
                        source_line=line
                    )
                if_stack.append(idx)

            # Block: END FOR / END FOREACH
            elif content.startswith(("END FOR", "END FOREACH")):
                if for_stack:
                    for_stack.pop()
                else:
                    return ErrorReport(
                        problem="Found an extra 'END FOR' without a matching 'FOR'.",
                        concept="END FOR closes a loop block, but no active loop was found.",
                        expected="FOR i ← 1 to N DO\n    ...\nEND FOR",
                        suggestion="Remove this redundant loop terminator.",
                        technical_error="SyntaxError: Unmatched 'END FOR'",
                        line_number=idx,
                        source_line=line
                    )
            # Block: FOR / FOREACH ... DO
            elif content.startswith(("FOR ", "FOREACH ")):
                if "DO" not in content:
                    return ErrorReport(
                        problem="The loop statement is missing 'DO'.",
                        concept="Loops in ExplainCode end their header line with 'DO'.",
                        expected="FOR i ← 1 to 10 DO\n    ...\nEND FOR",
                        suggestion="Add 'DO' at the end of the loop header.",
                        technical_error="SyntaxError: Missing DO in loop header",
                        line_number=idx,
                        source_line=line
                    )
                for_stack.append(idx)

            # Block: END WHILE
            elif content.startswith("END WHILE"):
                if while_stack:
                    while_stack.pop()
                else:
                    return ErrorReport(
                        problem="Found an extra 'END WHILE' without a matching 'WHILE'.",
                        concept="END WHILE closes a WHILE loop block, but no active loop was found.",
                        expected="WHILE condition DO\n    ...\nEND WHILE",
                        suggestion="Remove this redundant 'END WHILE'.",
                        technical_error="SyntaxError: Unmatched 'END WHILE'",
                        line_number=idx,
                        source_line=line
                    )
            # Block: WHILE ... DO
            elif content.startswith("WHILE ") or content == "WHILE":
                if "DO" not in content:
                    return ErrorReport(
                        problem="The loop statement is missing 'DO'.",
                        concept="WHILE loops end their header line with 'DO'.",
                        expected="WHILE condition DO\n    ...\nEND WHILE",
                        suggestion="Add 'DO' at the end of the WHILE header.",
                        technical_error="SyntaxError: Missing DO in WHILE header",
                        line_number=idx,
                        source_line=line
                    )
                while_stack.append(idx)

            # Block: END TRY
            elif content.startswith("END TRY"):
                if try_stack:
                    try_stack.pop()
                else:
                    return ErrorReport(
                        problem="Found 'END TRY' without a matching 'TRY'.",
                        concept="END TRY closes a TRY ... CATCH block.",
                        expected="TRY\n    ...\nCATCH error\n    ...\nEND TRY",
                        suggestion="Remove this redundant 'END TRY'.",
                        technical_error="SyntaxError: Unmatched 'END TRY'",
                        line_number=idx,
                        source_line=line
                    )
            # Block: TRY
            elif content.startswith("TRY"):
                try_stack.append(idx)


        # Unclosed blocks
        if if_stack:
            start_line = if_stack[-1]
            return ErrorReport(
                problem="The algorithm is missing END IF.",
                concept="Every IF block must eventually be closed with END IF.",
                expected="IF condition THEN\n    ...\nEND IF",
                suggestion=f"Add END IF after the conditional block that started on Line {start_line}.",
                technical_error=f"SyntaxError: Unclosed IF block starting at line {start_line}",
                line_number=start_line
            )

        if for_stack:
            start_line = for_stack[-1]
            return ErrorReport(
                problem="The algorithm is missing END FOR / END FOREACH.",
                concept="Every FOR or FOREACH loop must be closed with END FOR or END FOREACH.",
                expected="FOR i ← 1 to N DO\n    ...\nEND FOR",
                suggestion=f"Add END FOR after the loop block that started on Line {start_line}.",
                technical_error=f"SyntaxError: Unclosed loop block starting at line {start_line}",
                line_number=start_line
            )

        if while_stack:
            start_line = while_stack[-1]
            return ErrorReport(
                problem="The algorithm is missing END WHILE.",
                concept="Every WHILE loop must be closed with END WHILE.",
                expected="WHILE condition DO\n    ...\nEND WHILE",
                suggestion=f"Add END WHILE after the loop block that started on Line {start_line}.",
                technical_error=f"SyntaxError: Unclosed WHILE block starting at line {start_line}",
                line_number=start_line
            )

        if try_stack:
            start_line = try_stack[-1]
            return ErrorReport(
                problem="The algorithm is missing END TRY.",
                concept="Every TRY block must be closed with END TRY.",
                expected="TRY\n    ...\nCATCH error\n    ...\nEND TRY",
                suggestion=f"Add END TRY after the block that started on Line {start_line}.",
                technical_error=f"SyntaxError: Unclosed TRY block starting at line {start_line}",
                line_number=start_line
            )

        return None

    @staticmethod
    def diagnose_runtime(exc: Exception, current_statement: Optional[str] = None) -> ErrorReport:
        """Diagnoses runtime exceptions and returns structured beginner explanations."""
        err_type = type(exc).__name__
        err_msg = str(exc)

        if isinstance(exc, NameError):
            match = re.search(r"name '(\w+)' is not defined", err_msg)
            var = match.group(1) if match else "variable"
            return ErrorReport(
                problem=f"Variable '{var}' was used before it was given a value.",
                concept="Variables must be created or defined with SET or INPUT before they can be read.",
                expected=f"SET {var} ← 0\n... or ...\nINPUT: {var}",
                suggestion=f"Initialize '{var}' with SET before line where it is used.",
                technical_error=f"{err_type}: {err_msg}",
                source_line=current_statement
            )

        if isinstance(exc, ZeroDivisionError):
            return ErrorReport(
                problem="Attempted to divide a number by zero.",
                concept="Division by zero is mathematically undefined and causes computers to stop.",
                expected="IF divisor != 0 THEN\n    SET result ← number / divisor\nEND IF",
                suggestion="Add an IF check to verify the divisor is not zero before dividing.",
                technical_error=f"{err_type}: {err_msg}",
                source_line=current_statement
            )

        if isinstance(exc, IndexError):
            return ErrorReport(
                problem="Tried to access an item at an index that does not exist in the list.",
                concept="Lists are indexed starting at 0 up to len - 1. Accessing beyond that causes an IndexError.",
                expected="IF index < len(my_list) THEN\n    SET item ← my_list[index]\nEND IF",
                suggestion="Check the list length before indexing or adjust loop bounds.",
                technical_error=f"{err_type}: {err_msg}",
                source_line=current_statement
            )

        if isinstance(exc, KeyError):
            return ErrorReport(
                problem=f"Key {err_msg} was not found in the dictionary.",
                concept="Dictionaries store values under specific keys. You cannot read a key that has not been stored.",
                expected="DICT data ← {'key': value}\nGET data['key'] → result",
                suggestion="Check that the key name is spelled correctly and exists in the dictionary.",
                technical_error=f"{err_type}: {err_msg}",
                source_line=current_statement
            )

        if isinstance(exc, TypeError):
            if "not subscriptable" in err_msg:
                return ErrorReport(
                    problem="Tried to access an item using brackets [ ] on a value that is not a list or collection (such as an integer).",
                    concept="Indexing (e.g. A[0]) requires a collection such as a LIST (e.g. [12, 5, 8]). A single number cannot be indexed.",
                    expected="Pass a list with brackets: [12, 5, 8] or define: LIST A ← [12, 5, 8]",
                    suggestion="When entering inputs for lists, provide values enclosed in square brackets, e.g. [12, 5, 8].",
                    technical_error=f"{err_type}: {err_msg}",
                    source_line=current_statement
                )
            return ErrorReport(
                problem="Operation attempted on incompatible data types.",
                concept="Operations require matching types (for example, you cannot add text to a number directly).",
                expected="SET text ← str(number)  # or ensure both operands are numbers",
                suggestion="Check the types of the variables involved in this step.",
                technical_error=f"{err_type}: {err_msg}",
                source_line=current_statement
            )

        # General / Catch-all
        return ErrorReport(
            problem=f"An unexpected error occurred: {err_msg}",
            concept="The computer could not complete this operation.",
            expected="Inspect the current step and variable values in Program State.",
            suggestion="Review the technical error below to identify the issue.",
            technical_error=f"{err_type}: {err_msg}",
            source_line=current_statement
        )
