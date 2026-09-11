"""
Tests for Python code generation using ExplainCodeCompiler / ExplainAICompiler.
"""

import ast
import pytest
from explaincode.compiler import ExplainCodeCompiler, ExplainCodeParser, ExplainAICompiler, ExplainAIParser


def test_compiler_aliases():
    assert ExplainCodeCompiler is ExplainAICompiler
    assert ExplainCodeParser is ExplainAIParser


def test_compiler_basic_assignment_and_print():
    code = [
        "ALGORITHM SimpleAdd",
        "INPUT: a, b",
        "STEP 1: Set result ← a + b",
        "STEP 2: PRINT result",
        "STEP 3: RETURN result",
        "END ALGORITHM"
    ]
    parser = ExplainCodeParser()
    ast_tree = parser.parse(code)
    compiler = ExplainCodeCompiler(ast_tree)
    py_code = compiler.compile()

    assert "def SimpleAdd(a, b):" in py_code
    assert "result = a + b" in py_code
    assert "print(result)" in py_code
    assert "return result" in py_code

    # Verify generated Python is valid AST
    tree = ast.parse(py_code)
    assert tree is not None


def test_compiler_conditionals():
    code = [
        "ALGORITHM CheckSign",
        "INPUT: x",
        "STEP 1: IF x > 0 THEN",
        "STEP 2:     DISPLAY \"Positive\"",
        "STEP 3: ELSE",
        "STEP 4:     DISPLAY \"Negative\"",
        "STEP 5: END IF",
        "END ALGORITHM"
    ]
    parser = ExplainCodeParser()
    ast_tree = parser.parse(code)
    compiler = ExplainCodeCompiler(ast_tree)
    py_code = compiler.compile()

    assert "if x > 0:" in py_code
    assert "else:" in py_code
    assert "print(\"Positive\")" in py_code
    assert "print(\"Negative\")" in py_code

    local_scope = {}
    exec(py_code, {}, local_scope)
    assert "CheckSign" in local_scope


def test_compiler_loops_and_control():
    code = [
        "ALGORITHM LoopTest",
        "INPUT: n",
        "STEP 1: FOR i ← 1 to n DO",
        "STEP 2:     IF i == 3 THEN",
        "STEP 3:         CONTINUE",
        "STEP 4:     END IF",
        "STEP 5:     PRINT i",
        "STEP 6: END FOR",
        "END ALGORITHM"
    ]
    parser = ExplainCodeParser()
    ast_tree = parser.parse(code)
    compiler = ExplainCodeCompiler(ast_tree)
    py_code = compiler.compile()

    assert "for i in range(1, n+1):" in py_code
    assert "continue" in py_code


def test_compiler_data_structures():
    code = [
        "ALGORITHM DataTest",
        "INPUT:",
        "STEP 1: LIST items ← [1, 2, 3]",
        "STEP 2: APPEND items ← 4",
        "STEP 3: REMOVE items ← 1",
        "STEP 4: DICT d ← {\"k\": 10}",
        "STEP 5: GET d[\"k\"] → val",
        "STEP 6: RETURN val",
        "END ALGORITHM"
    ]
    parser = ExplainCodeParser()
    ast_tree = parser.parse(code)
    compiler = ExplainCodeCompiler(ast_tree)
    py_code = compiler.compile()

    local_scope = {}
    exec(py_code, {}, local_scope)
    assert local_scope["DataTest"]() == 10


def test_compiler_functional_utilities():
    code = [
        "ALGORITHM FuncTest",
        "INPUT: nums",
        "STEP 1: SORT nums → sorted_nums",
        "STEP 2: FILTER sorted_nums WHERE x > 5 → filtered",
        "STEP 3: MAP filtered WITH x * 10 → mapped",
        "STEP 4: RETURN mapped",
        "END ALGORITHM"
    ]
    parser = ExplainCodeParser()
    ast_tree = parser.parse(code)
    compiler = ExplainCodeCompiler(ast_tree)
    py_code = compiler.compile()

    assert "sorted(nums)" in py_code
    assert "[_x for _x in sorted_nums if _x > 5]" in py_code
    assert "[_x * 10 for _x in filtered]" in py_code

    local_scope = {}
    exec(py_code, {}, local_scope)
    res = local_scope["FuncTest"]([8, 2, 6, 1])
    assert res == [60, 80]
