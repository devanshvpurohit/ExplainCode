"""
Tests for ExplainCode concept detection and explanations.
"""

import pytest
from explaincode.compiler import ExplainCodeParser
from explaincode.concepts import ConceptExplainer, explain_code, CONCEPT_DEFINITIONS


def test_concept_definitions_coverage():
    """Verify all required concepts exist in CONCEPT_DEFINITIONS."""
    required = [
        "variables", "assignment", "input", "output",
        "if_conditional", "for_loop", "foreach_loop", "while_loop",
        "break", "continue", "lists", "dictionaries",
        "functions", "return", "error_handling", "map", "filter", "reduce"
    ]
    for req in required:
        assert req in CONCEPT_DEFINITIONS, f"Missing required concept definition: {req}"
        assert "title" in CONCEPT_DEFINITIONS[req]
        assert "description" in CONCEPT_DEFINITIONS[req]
        assert "python_equivalent" in CONCEPT_DEFINITIONS[req]


def test_variable_and_assignment_concept():
    code = [
        "ALGORITHM AssignDemo",
        "INPUT: x",
        "STEP 1: Set total == 0",
        "STEP 2: PRINT total",
        "STEP 3: RETURN total",
        "END ALGORITHM"
    ]
    parser = ExplainCodeParser()
    ast = parser.parse(code)

    explainer = ConceptExplainer()
    concepts = explainer.explain_ast(ast)
    titles = [c["title"] for c in concepts]

    assert "Variable Assignment" in titles
    assert "Variables" in titles
    assert "User / Function Input (Parameters)" in titles
    assert "Output (PRINT / DISPLAY)" in titles
    assert "Return Value" in titles


def test_conditional_concept():
    code = [
        "ALGORITHM CheckScore",
        "INPUT: score",
        "STEP 1: IF score > 50 THEN",
        "STEP 2:     DISPLAY \"Pass\"",
        "STEP 3: ELSE",
        "STEP 4:     DISPLAY \"Fail\"",
        "STEP 5: END IF",
        "END ALGORITHM"
    ]
    parser = ExplainCodeParser()
    ast = parser.parse(code)

    explainer = ConceptExplainer()
    concepts = explainer.explain_ast(ast)
    titles = [c["title"] for c in concepts]

    assert "Conditional Statement (IF / ELSE)" in titles
    formatted = explainer.format_explanations_text(concepts)
    assert "decision based on whether a condition is true or false" in formatted


def test_loops_break_continue_concepts():
    code = [
        "ALGORITHM LoopDemo",
        "INPUT: limit",
        "STEP 1: FOR i == 1 to 10 DO",
        "STEP 2:     IF i == 5 THEN",
        "STEP 3:         CONTINUE",
        "STEP 4:     END IF",
        "STEP 5:     PRINT i",
        "STEP 6: END FOR",
        "STEP 7: FOREACH item IN [1, 2, 3] DO",
        "STEP 8:     PRINT item",
        "STEP 9: END FOREACH",
        "STEP 10: WHILE limit > 0 DO",
        "STEP 11:    Set limit == limit - 1",
        "STEP 12:    IF limit == 0 THEN",
        "STEP 13:        BREAK",
        "STEP 14:    END IF",
        "STEP 15: END WHILE",
        "END ALGORITHM"
    ]
    parser = ExplainCodeParser()
    ast = parser.parse(code)

    explainer = ConceptExplainer()
    concepts = explainer.explain_ast(ast)
    titles = [c["title"] for c in concepts]

    assert "FOR Loop (Range / Counting)" in titles
    assert "FOREACH Loop (Collection Iteration)" in titles
    assert "WHILE Loop (Conditional Iteration)" in titles
    assert "BREAK Statement" in titles
    assert "CONTINUE Statement" in titles


def test_data_structures_and_functional_concepts():
    code = [
        "ALGORITHM DataProc",
        "INPUT: items",
        "STEP 1: LIST nums == [1, 2, 3]",
        "STEP 2: APPEND nums == 4",
        "STEP 3: REMOVE nums == 1",
        "STEP 4: DICT user == {\"name\": \"Bob\"}",
        "STEP 5: GET user[\"name\"] → uname",
        "STEP 6: MAP nums WITH x * 2 → doubled",
        "STEP 7: FILTER nums WHERE x > 2 → filtered",
        "STEP 8: REDUCE nums WITH acc + x → total",
        "STEP 9: RETURN total",
        "END ALGORITHM"
    ]
    parser = ExplainCodeParser()
    ast = parser.parse(code)

    explainer = ConceptExplainer()
    concepts = explainer.explain_ast(ast)
    titles = [c["title"] for c in concepts]

    assert "Lists (Ordered Collections)" in titles
    assert "Dictionaries (Key-Value Pairs)" in titles
    assert "MAP Operation (Transformation)" in titles
    assert "FILTER Operation (Selection)" in titles
    assert "REDUCE Operation (Aggregation)" in titles


def test_error_handling_and_functions_concept():
    code = [
        "ALGORITHM SafeCaller",
        "INPUT: a, b",
        "STEP 1: TRY",
        "STEP 2:     CALL compute(a, b) → res",
        "STEP 3: CATCH err",
        "STEP 4:     Set res == 0",
        "STEP 5: END TRY",
        "STEP 6: RETURN res",
        "END ALGORITHM"
    ]
    parser = ExplainCodeParser()
    ast = parser.parse(code)

    explainer = ConceptExplainer()
    concepts = explainer.explain_ast(ast)
    titles = [c["title"] for c in concepts]

    assert "Error Handling (TRY / CATCH)" in titles
    assert "Function / Algorithm Definition & Calls" in titles

    summary_text = explain_code(ast)
    assert "TRY / CATCH" in summary_text
