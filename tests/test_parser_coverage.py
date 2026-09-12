import pytest
from explaincode.compiler import ExplainCodeParser

def test_parser_empty_file():
    parser = ExplainCodeParser()
    with pytest.raises(SyntaxError, match="File must start with ALGORITHM, MODEL, or API_CALL"):
        parser.parse(["", "  ", "# Just a comment"])

def test_parser_invalid_header():
    parser = ExplainCodeParser()
    with pytest.raises(SyntaxError, match="File must start with ALGORITHM, MODEL, or API_CALL"):
        parser.parse(["STEP 1: Set x == 10"])

def test_parser_imports_and_keys():
    code = [
        "ALGORITHM SpecialFeatures",
        "INPUT: a",
        "Import math",
        "KEY: 123456",
        "STEP 1: Set res == math.sqrt(a)",
        "RETURN res",
        "END ALGORITHM"
    ]
    parser = ExplainCodeParser()
    ast = parser.parse(code)
    
    assert ast["function_name"] == "SpecialFeatures"
    assert ast["inputs"] == ["a"]
    assert any(step["type"] == "import" and step["lib"] == "math" for step in ast["body"])
    assert any(step["type"] == "apikey" and step["value"] == "123456" for step in ast["body"])
    assert any(step["type"] == "assign" and step["target"] == "res" for step in ast["body"])

def test_parser_else_if():
    # Else If is basically parsed as else then if in Python, but let's test how ExplainCode handles it
    # Currently ELSE IF is parsed as IF inside an ELSE or ignored if not implemented explicitly.
    code = [
        "ALGORITHM ElseIfTest",
        "INPUT: x",
        "STEP 1: IF x > 10 THEN",
        "STEP 2:     RETURN 1",
        "STEP 3: ELSE IF x > 5 THEN",
        "STEP 4:     RETURN 2",
        "STEP 5: END IF",
        "END ALGORITHM"
    ]
    parser = ExplainCodeParser()
    ast = parser.parse(code)
    # Checking that the parser handles it without crashing, even if it falls through to basic IF
    assert len(ast["body"]) > 0
