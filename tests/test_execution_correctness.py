import pytest
from explaincode.compiler import ExplainCodeCompiler, ExplainCodeParser
from explaincode.stepper import ExplainCodeStepper

def test_fibonacci_execution():
    code = [
        "ALGORITHM Fibonacci",
        "INPUT: n",
        "STEP 1: SET sequence == []",
        "STEP 2: sequence.append(0)",
        "STEP 3: sequence.append(1)",
        "STEP 4: FOR i == 2 to n-1 DO",
        "STEP 5:     SET next_val == sequence[i-1] + sequence[i-2]",
        "STEP 6:     sequence.append(next_val)",
        "STEP 7: END FOR",
        "STEP 8: RETURN sequence",
        "END ALGORITHM"
    ]
    parser = ExplainCodeParser()
    ast = parser.parse(code)
    
    # Test via stepper (execution correctness)
    stepper = ExplainCodeStepper(ast, initial_inputs={"n": 5})
    stepper.run_all()
    assert stepper.return_value == [0, 1, 1, 2, 3]

def test_fizzbuzz_compilation_correctness():
    code = [
        "ALGORITHM FizzBuzz",
        "INPUT: n",
        "STEP 1: SET result_list == []",
        "STEP 2: FOR i == 1 to n DO",
        "STEP 3:     IF i % 3 == 0 THEN",
        "STEP 4:         result_list.append(\"Fizz\")",
        "STEP 5:     ELSE",
        "STEP 6:         result_list.append(i)",
        "STEP 7:     END IF",
        "STEP 8: END FOR",
        "STEP 9: RETURN result_list",
        "END ALGORITHM"
    ]
    parser = ExplainCodeParser()
    ast = parser.parse(code)
    compiler = ExplainCodeCompiler(ast)
    py_code = compiler.compile()
    
    local_scope = {}
    exec(py_code, {}, local_scope)
    res = local_scope["FizzBuzz"](4)
    assert res == [1, 2, "Fizz", 4]
