"""
explaincode.concepts

Analyzes parsed ExplainCode AST and explains programming concepts used.
Maps AST nodes and code structures to beginner-friendly explanations,
illustrating algorithmic thinking and connecting it to Python equivalents.
"""

from typing import List, Dict, Any, Optional

CONCEPT_DEFINITIONS = {
    "variables": {
        "title": "Variables",
        "category": "Data Storage",
        "description": "Variables are named containers used to store data values in memory that your program can read and change later.",
        "python_equivalent": "In Python, variables are created automatically when you assign a value: x = 10"
    },
    "assignment": {
        "title": "Variable Assignment",
        "category": "Data Storage",
        "description": "SET creates or updates a variable and assigns it an initial or new value using the arrow '←'.",
        "python_equivalent": "Python uses the '=' symbol for assignment: variable_name = value"
    },
    "input": {
        "title": "User / Function Input (Parameters)",
        "category": "Data Input",
        "description": "INPUT defines the parameters or values that must be provided to the algorithm for it to execute.",
        "python_equivalent": "In Python, inputs to functions are defined as parameter arguments: def algorithm(arg1, arg2): or input() for console input."
    },
    "output": {
        "title": "Output (PRINT / DISPLAY)",
        "category": "Communication",
        "description": "PRINT / DISPLAY outputs data, messages, or variable values to the user or console.",
        "python_equivalent": "In Python, output is displayed using the print(...) function."
    },
    "if_conditional": {
        "title": "Conditional Statement (IF / ELSE)",
        "category": "Control Flow",
        "description": "An IF statement allows a program to make a decision based on whether a condition is true or false.",
        "python_equivalent": "Python uses 'if condition:' and 'else:' indented blocks."
    },
    "for_loop": {
        "title": "FOR Loop (Range / Counting)",
        "category": "Control Flow",
        "description": "A FOR loop repeats a block of code a specific number of times as a counter progresses from start to end.",
        "python_equivalent": "In Python, counting loops use range(): for i in range(start, end + 1):"
    },
    "foreach_loop": {
        "title": "FOREACH Loop (Collection Iteration)",
        "category": "Control Flow",
        "description": "A FOREACH loop iterates over each item in a collection (like a list) one by one.",
        "python_equivalent": "In Python, iterating over a list uses: for item in collection:"
    },
    "while_loop": {
        "title": "WHILE Loop (Conditional Iteration)",
        "category": "Control Flow",
        "description": "A WHILE loop repeats a block of code as long as a specified condition remains true.",
        "python_equivalent": "In Python, conditional iteration uses: while condition:"
    },
    "break": {
        "title": "BREAK Statement",
        "category": "Control Flow",
        "description": "BREAK immediately stops and exits the currently active loop, regardless of remaining iterations.",
        "python_equivalent": "In Python, 'break' exits the current loop immediately."
    },
    "continue": {
        "title": "CONTINUE Statement",
        "category": "Control Flow",
        "description": "CONTINUE skips the rest of the current loop iteration and moves directly to the next iteration.",
        "python_equivalent": "In Python, 'continue' skips to the next loop cycle."
    },
    "lists": {
        "title": "Lists (Ordered Collections)",
        "category": "Data Structures",
        "description": "A LIST holds an ordered collection of values that can be modified, appended to, or accessed by index.",
        "python_equivalent": "In Python, lists are created with brackets: my_list = [1, 2, 3] and support .append() and .remove()."
    },
    "dictionaries": {
        "title": "Dictionaries (Key-Value Pairs)",
        "category": "Data Structures",
        "description": "A DICT stores data in key-value pairs, allowing fast retrieval of information using descriptive keys.",
        "python_equivalent": "In Python, dictionaries use curly braces: person = {'name': 'Alice', 'age': 20} and person['name']."
    },
    "functions": {
        "title": "Function / Algorithm Definition & Calls",
        "category": "Modular Code",
        "description": "Algorithms and CALL statements organize code into reusable blocks that can take arguments and return results.",
        "python_equivalent": "Python defines reusable functions with 'def name(params):' and calls them using name(args)."
    },
    "return": {
        "title": "Return Value",
        "category": "Control Flow",
        "description": "RETURN sends a computed result back from an algorithm or function to whoever called it.",
        "python_equivalent": "In Python, 'return value' passes the result back and terminates function execution."
    },
    "error_handling": {
        "title": "Error Handling (TRY / CATCH)",
        "category": "Robustness",
        "description": "TRY / CATCH allows programs to handle unexpected errors gracefully without crashing.",
        "python_equivalent": "In Python, this is done with 'try:' and 'except Exception as err:' blocks."
    },
    "map": {
        "title": "MAP Operation (Transformation)",
        "category": "Functional Programming",
        "description": "MAP applies an expression or transformation to every element in a list, creating a new transformed list.",
        "python_equivalent": "In Python, this is typically done using list comprehensions: [expr for x in list] or map()."
    },
    "filter": {
        "title": "FILTER Operation (Selection)",
        "category": "Functional Programming",
        "description": "FILTER selects only the elements in a collection that satisfy a given true/false condition.",
        "python_equivalent": "In Python, this is typically done using: [x for x in list if condition] or filter()."
    },
    "reduce": {
        "title": "REDUCE Operation (Aggregation)",
        "category": "Functional Programming",
        "description": "REDUCE aggregates all elements of a list into a single accumulated result using an expression.",
        "python_equivalent": "In Python, from functools import reduce; reduce(lambda acc, x: expr, list)"
    },
    "ai_pipeline": {
        "title": "AI & Machine Learning Pipeline",
        "category": "Artificial Intelligence",
        "description": "AI operations load pre-trained neural network models and execute predictions on user inputs.",
        "python_equivalent": "In Python, using Hugging Face transformers pipeline: model = pipeline('task'); result = model(text)"
    }
}


class ConceptExplainer:
    """Analyzes AST and generates detailed concept explanations."""

    def __init__(self):
        pass

    def explain_ast(self, ast_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Takes an ExplainCode AST dictionary and returns a list of detected concepts
        with explanations tailored to the specific code.
        """
        detected: Dict[str, Dict[str, Any]] = {}

        # 1. Inputs / Parameters
        inputs = ast_dict.get("inputs", [])
        if inputs:
            detected["input"] = {
                **CONCEPT_DEFINITIONS["input"],
                "details": f"This algorithm accepts input parameter(s): {', '.join(inputs)}.",
                "examples_in_code": [f"INPUT: {', '.join(inputs)}"]
            }

        # 2. Algorithm / Function
        fn_name = ast_dict.get("function_name", "")
        if fn_name:
            detected["functions"] = {
                **CONCEPT_DEFINITIONS["functions"],
                "details": f"Defined algorithm or function '{fn_name}' which wraps this logic into a callable unit.",
                "examples_in_code": [f"ALGORITHM {fn_name}"]
            }

        # 3. Analyze Body Statements
        body = ast_dict.get("body", [])
        for stmt in body:
            stype = stmt.get("type")

            if stype == "assign":
                if "assignment" not in detected:
                    detected["assignment"] = {
                        **CONCEPT_DEFINITIONS["assignment"],
                        "details": "Variables are being assigned new values.",
                        "examples_in_code": []
                    }
                detected["assignment"]["examples_in_code"].append(
                    f"Set {stmt.get('target')} ← {stmt.get('value')}"
                )
                if "variables" not in detected:
                    detected["variables"] = {
                        **CONCEPT_DEFINITIONS["variables"],
                        "details": f"Stores state such as variable '{stmt.get('target')}'.",
                        "examples_in_code": [str(stmt.get('target'))]
                    }

            elif stype == "print":
                if "output" not in detected:
                    detected["output"] = {
                        **CONCEPT_DEFINITIONS["output"],
                        "details": "The program displays output messages or values.",
                        "examples_in_code": []
                    }
                detected["output"]["examples_in_code"].append(f"PRINT {stmt.get('value')}")

            elif stype in ("if", "else", "endif"):
                if "if_conditional" not in detected:
                    cond = stmt.get("condition", "condition")
                    detected["if_conditional"] = {
                        **CONCEPT_DEFINITIONS["if_conditional"],
                        "details": f"Branching decision based on condition: {cond}.",
                        "examples_in_code": []
                    }
                if stype == "if":
                    detected["if_conditional"]["examples_in_code"].append(f"IF {stmt.get('condition')} THEN")

            elif stype in ("for", "endfor"):
                if "for_loop" not in detected:
                    detected["for_loop"] = {
                        **CONCEPT_DEFINITIONS["for_loop"],
                        "details": f"Repeats logic with loop counter '{stmt.get('var', 'i')}' from {stmt.get('start', '0')} to {stmt.get('end', 'N')}.",
                        "examples_in_code": []
                    }
                if stype == "for":
                    detected["for_loop"]["examples_in_code"].append(
                        f"FOR {stmt.get('var')} ← {stmt.get('start')} to {stmt.get('end')} DO"
                    )

            elif stype in ("foreach", "endforeach"):
                if "foreach_loop" not in detected:
                    detected["foreach_loop"] = {
                        **CONCEPT_DEFINITIONS["foreach_loop"],
                        "details": f"Iterates over each element in '{stmt.get('iterable', 'collection')}'.",
                        "examples_in_code": []
                    }
                if stype == "foreach":
                    detected["foreach_loop"]["examples_in_code"].append(
                        f"FOREACH {stmt.get('var')} IN {stmt.get('iterable')} DO"
                    )

            elif stype in ("while", "endwhile"):
                if "while_loop" not in detected:
                    detected["while_loop"] = {
                        **CONCEPT_DEFINITIONS["while_loop"],
                        "details": f"Repeats while condition '{stmt.get('condition', 'expr')}' is true.",
                        "examples_in_code": []
                    }
                if stype == "while":
                    detected["while_loop"]["examples_in_code"].append(
                        f"WHILE {stmt.get('condition')} DO"
                    )

            elif stype == "break":
                if "break" not in detected:
                    detected["break"] = {
                        **CONCEPT_DEFINITIONS["break"],
                        "details": "Terminates loop prematurely upon reaching this statement.",
                        "examples_in_code": ["BREAK"]
                    }

            elif stype == "continue":
                if "continue" not in detected:
                    detected["continue"] = {
                        **CONCEPT_DEFINITIONS["continue"],
                        "details": "Jumps directly to the next iteration of the loop.",
                        "examples_in_code": ["CONTINUE"]
                    }

            elif stype in ("list_create", "list_append", "list_remove"):
                if "lists" not in detected:
                    detected["lists"] = {
                        **CONCEPT_DEFINITIONS["lists"],
                        "details": "Manipulates a list data structure.",
                        "examples_in_code": []
                    }
                if stype == "list_create":
                    detected["lists"]["examples_in_code"].append(f"LIST {stmt.get('name')} ← {stmt.get('value')}")
                elif stype == "list_append":
                    detected["lists"]["examples_in_code"].append(f"APPEND {stmt.get('list_name')} ← {stmt.get('value')}")
                elif stype == "list_remove":
                    detected["lists"]["examples_in_code"].append(f"REMOVE {stmt.get('list_name')} ← {stmt.get('value')}")

            elif stype in ("dict_create", "get_value"):
                if "dictionaries" not in detected:
                    detected["dictionaries"] = {
                        **CONCEPT_DEFINITIONS["dictionaries"],
                        "details": "Manipulates key-value dictionary data structures.",
                        "examples_in_code": []
                    }
                if stype == "dict_create":
                    detected["dictionaries"]["examples_in_code"].append(f"DICT {stmt.get('name')} ← {stmt.get('value')}")
                elif stype == "get_value":
                    detected["dictionaries"]["examples_in_code"].append(f"GET {stmt.get('source')} → {stmt.get('target')}")

            elif stype == "call":
                if "functions" not in detected:
                    detected["functions"] = {
                        **CONCEPT_DEFINITIONS["functions"],
                        "details": f"Calls function '{stmt.get('func_name')}'.",
                        "examples_in_code": []
                    }
                detected["functions"]["examples_in_code"].append(
                    f"CALL {stmt.get('func_name')}({', '.join(stmt.get('args', []))})"
                )

            elif stype == "return":
                if "return" not in detected:
                    detected["return"] = {
                        **CONCEPT_DEFINITIONS["return"],
                        "details": f"Returns value: {stmt.get('value')}.",
                        "examples_in_code": []
                    }
                detected["return"]["examples_in_code"].append(f"RETURN {stmt.get('value')}")

            elif stype in ("try", "catch", "endtry"):
                if "error_handling" not in detected:
                    detected["error_handling"] = {
                        **CONCEPT_DEFINITIONS["error_handling"],
                        "details": "Catches potential runtime exceptions to prevent program crash.",
                        "examples_in_code": []
                    }
                if stype == "try":
                    detected["error_handling"]["examples_in_code"].append("TRY ... CATCH")

            elif stype == "map":
                if "map" not in detected:
                    detected["map"] = {
                        **CONCEPT_DEFINITIONS["map"],
                        "details": f"Transforms each element of '{stmt.get('source')}' with expression '{stmt.get('expression')}'.",
                        "examples_in_code": [f"MAP {stmt.get('source')} WITH {stmt.get('expression')} → {stmt.get('target')}"]
                    }

            elif stype == "filter":
                if "filter" not in detected:
                    detected["filter"] = {
                        **CONCEPT_DEFINITIONS["filter"],
                        "details": f"Filters '{stmt.get('source')}' where '{stmt.get('condition')}'.",
                        "examples_in_code": [f"FILTER {stmt.get('source')} WHERE {stmt.get('condition')} → {stmt.get('target')}"]
                    }

            elif stype == "reduce":
                if "reduce" not in detected:
                    detected["reduce"] = {
                        **CONCEPT_DEFINITIONS["reduce"],
                        "details": f"Reduces '{stmt.get('source')}' using accumulator expression '{stmt.get('expression')}'.",
                        "examples_in_code": [f"REDUCE {stmt.get('source')} WITH {stmt.get('expression')} → {stmt.get('target')}"]
                    }

            elif stype in ("load_model", "predict", "train"):
                if "ai_pipeline" not in detected:
                    detected["ai_pipeline"] = {
                        **CONCEPT_DEFINITIONS["ai_pipeline"],
                        "details": "Employs machine learning pipeline models.",
                        "examples_in_code": []
                    }
                if stype == "load_model":
                    detected["ai_pipeline"]["examples_in_code"].append(f"LOAD_MODEL \"{stmt.get('model_name')}\"")
                elif stype == "predict":
                    detected["ai_pipeline"]["examples_in_code"].append(f"PREDICT {stmt.get('input')} → {stmt.get('output')}")

        return list(detected.values())

    def format_explanations_text(self, concepts: List[Dict[str, Any]]) -> str:
        """Formats detected concepts into a structured readable summary."""
        if not concepts:
            return "No programming concepts detected. Write some ExplainCode to see explanations!"

        lines = ["💡 PROGRAMMING CONCEPTS USED IN THIS ALGORITHM:\n"]
        for idx, c in enumerate(concepts, 1):
            lines.append(f"{idx}. CONCEPT: {c['title']} ({c.get('category', 'General')})")
            lines.append(f"   \"{c['description']}\"")
            if c.get("details"):
                lines.append(f"   In your code: {c['details']}")
            if c.get("python_equivalent"):
                lines.append(f"   🐍 Python equivalent: {c['python_equivalent']}")
            if c.get("examples_in_code"):
                exs = c["examples_in_code"][:3]
                lines.append(f"   Code examples: {', '.join(exs)}")
            lines.append("")
        return "\n".join(lines)


def explain_code(ast_dict: Dict[str, Any]) -> str:
    """Convenience function to get formatted explanation from AST."""
    explainer = ConceptExplainer()
    concepts = explainer.explain_ast(ast_dict)
    return explainer.format_explanations_text(concepts)
