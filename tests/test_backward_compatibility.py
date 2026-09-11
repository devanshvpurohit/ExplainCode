"""
Tests verifying that all existing ExplainCode features, examples, compiler, interpreter,
and APIs remain backward-compatible and functional.
"""

import os
import glob
import pytest
from explaincode.compiler import ExplainAIParser, ExplainAICompiler, ExplainCodeParser, ExplainCodeCompiler
from explaincode.interpreter import ExplainCodeInterpreter


def test_existing_find_max_example():
    epd_file = os.path.join(os.path.dirname(__file__), "..", "examples", "find_max.epd")
    with open(epd_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    parser = ExplainCodeParser()
    ast = parser.parse(lines)
    assert ast["function_name"] == "FindMax"

    compiler = ExplainCodeCompiler(ast)
    py_code = compiler.compile()
    assert "def FindMax(A, n):" in py_code

    # Run using existing interpreter
    outputs = []
    inputs = {"A": [3, 7, 2, 9, 5], "n": 5}
    def mock_input(prompt):
        for k, v in inputs.items():
            if k in prompt:
                return str(v), True
        return "0", True

    interp = ExplainCodeInterpreter(ast, gui_print_fn=outputs.append, gui_input_fn=mock_input)
    res = interp.run()
    assert res == 9


def test_existing_data_structures_example():
    epd_file = os.path.join(os.path.dirname(__file__), "..", "examples", "data_structures.epd")
    with open(epd_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    parser = ExplainCodeParser()
    ast = parser.parse(lines)
    assert ast["function_name"] == "DataStructuresDemo"

    compiler = ExplainCodeCompiler(ast)
    py_code = compiler.compile()
    assert "def DataStructuresDemo(name):" in py_code

    outputs = []
    inputs = {"name": "TestUser"}
    def mock_input(prompt):
        return "TestUser", True

    interp = ExplainCodeInterpreter(ast, gui_print_fn=outputs.append, gui_input_fn=mock_input)
    res = interp.run()
    assert res == "Data structures demo complete!"


def test_existing_loops_demo_example():
    epd_file = os.path.join(os.path.dirname(__file__), "..", "examples", "loops_demo.epd")
    with open(epd_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    parser = ExplainCodeParser()
    ast = parser.parse(lines)

    compiler = ExplainCodeCompiler(ast)
    py_code = compiler.compile()
    assert "def LoopsDemo(limit):" in py_code

    outputs = []
    def mock_input(prompt):
        return "5", True

    interp = ExplainCodeInterpreter(ast, gui_print_fn=outputs.append, gui_input_fn=mock_input)
    res = interp.run()
    assert res == 5


def test_existing_error_handling_example():
    epd_file = os.path.join(os.path.dirname(__file__), "..", "examples", "error_handling.epd")
    with open(epd_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    parser = ExplainCodeParser()
    ast = parser.parse(lines)

    compiler = ExplainCodeCompiler(ast)
    py_code = compiler.compile()
    assert "def ErrorHandlingDemo(x, y):" in py_code

    outputs = []
    # Test division by zero caught by TRY/CATCH
    inputs = [("10", True), ("0", True)]
    def mock_input(prompt):
        return inputs.pop(0)

    interp = ExplainCodeInterpreter(ast, gui_print_fn=outputs.append, gui_input_fn=mock_input)
    res = interp.run()
    assert res == 0


def test_gui_app_instantiation():
    """Verify ExplainCodeApp can be created without error."""
    import sys
    from PyQt5.QtWidgets import QApplication
    from explaincode.interpreter import ExplainCodeApp

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    window = ExplainCodeApp()
    assert window is not None
    assert hasattr(window, "editor")
    assert hasattr(window, "output")
    assert hasattr(window, "python_view")
    assert hasattr(window, "state_widget")
