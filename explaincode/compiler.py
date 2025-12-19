# explainai_compiler.py

import re
import sys
import os
import ast
import importlib
import argparse

# ------------------------------
# ExplainAI Parser + Compiler
# ------------------------------

class ExplainAIParser:
    def __init__(self):
        self.ast = {
            "function_name": "",
            "inputs": [],
            "body": []
        }

    def parse(self, lines):
        lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]

        if not lines[0].startswith(("ALGORITHM", "MODEL", "API_CALL")):
            raise SyntaxError("File must start with ALGORITHM, MODEL, or API_CALL.")

        self.ast["function_name"] = lines[0].split()[1]

        for line in lines[1:]:
            if line.startswith("INPUT:"):
                self.ast["inputs"] = [x.strip() for x in line.replace("INPUT:", "").split(",")]
            elif line.startswith("OUTPUT:"):
                continue  # Optional
            elif line.startswith(("END ALGORITHM", "END MODEL", "END API_CALL")):
                break
            elif line.startswith("STEP"):
                step = self._parse_step(line)
                if step:
                    self.ast["body"].append(step)

        return self.ast

    def _parse_step(self, line):
        match = re.match(r"STEP\s+\d+:?\s*(.+)", line)
        if not match:
            return None
        content = match.group(1)

        # === ASSIGNMENT ===
        if content.startswith("Set"):
            m = re.match(r"Set\s+(.+?)\s+←\s+(.+)", content)
            if m:
                return {"type": "assign", "target": m.group(1), "value": m.group(2)}

        # === IMPORTS ===
        elif content.startswith("Import"):
            return {"type": "import", "lib": content.split()[1]}

        elif content.startswith("KEY:"):
            return {"type": "apikey", "value": content.replace("KEY:", "").strip()}

        # === CONTROL FLOW ===
        elif content.startswith("FOREACH"):
            m = re.match(r"FOREACH\s+(\w+)\s+IN\s+(.+?)\s+DO", content)
            if m:
                return {"type": "foreach", "var": m.group(1), "iterable": m.group(2)}

        elif content.startswith("FOR"):
            m = re.match(r"FOR\s+(.+?)\s+←\s+(.+?)\s+to\s+(.+?)\s+DO", content)
            if m:
                return {"type": "for", "var": m.group(1), "start": m.group(2), "end": m.group(3)}

        elif content.startswith("WHILE"):
            condition = content.replace("WHILE", "").replace("DO", "").strip()
            return {"type": "while", "condition": condition}

        elif content.startswith("IF"):
            condition = content.replace("IF", "").replace("THEN", "").strip()
            return {"type": "if", "condition": condition}

        elif content.startswith("END IF"):
            return {"type": "endif"}

        elif content.startswith("ELSE"):
            return {"type": "else"}

        elif content.startswith("END FOREACH"):
            return {"type": "endforeach"}

        elif content.startswith("END FOR"):
            return {"type": "endfor"}

        elif content.startswith("END WHILE"):
            return {"type": "endwhile"}

        elif content.startswith("RETURN"):
            return {"type": "return", "value": content.replace("RETURN", "").strip()}

        elif content.startswith("PRINT"):
            return {"type": "print", "value": content.replace("PRINT", "").strip()}

        elif content.startswith("BREAK"):
            return {"type": "break"}

        elif content.startswith("CONTINUE"):
            return {"type": "continue"}

        # === DATA STRUCTURES ===
        elif content.startswith("LIST"):
            m = re.match(r"LIST\s+(\w+)\s+←\s+(.+)", content)
            if m:
                return {"type": "list_create", "name": m.group(1), "value": m.group(2)}

        elif content.startswith("DICT"):
            m = re.match(r"DICT\s+(\w+)\s+←\s+(.+)", content)
            if m:
                return {"type": "dict_create", "name": m.group(1), "value": m.group(2)}

        elif content.startswith("APPEND"):
            m = re.match(r"APPEND\s+(\w+)\s+←\s+(.+)", content)
            if m:
                return {"type": "list_append", "list_name": m.group(1), "value": m.group(2)}

        elif content.startswith("REMOVE"):
            m = re.match(r"REMOVE\s+(\w+)\s+←\s+(.+)", content)
            if m:
                return {"type": "list_remove", "list_name": m.group(1), "value": m.group(2)}

        elif content.startswith("GET"):
            m = re.match(r"GET\s+(.+?)\s+→\s+(\w+)", content)
            if m:
                return {"type": "get_value", "source": m.group(1), "target": m.group(2)}

        # === UTILITIES ===
        elif content.startswith("SORT"):
            m = re.match(r"SORT\s+(\w+)\s*(?:→\s*(\w+))?", content)
            if m:
                return {"type": "sort", "source": m.group(1), "target": m.group(2) or m.group(1)}

        elif content.startswith("FILTER"):
            m = re.match(r"FILTER\s+(\w+)\s+WHERE\s+(.+?)\s+→\s+(\w+)", content)
            if m:
                return {"type": "filter", "source": m.group(1), "condition": m.group(2), "target": m.group(3)}

        elif content.startswith("MAP"):
            m = re.match(r"MAP\s+(\w+)\s+WITH\s+(.+?)\s+→\s+(\w+)", content)
            if m:
                return {"type": "map", "source": m.group(1), "expression": m.group(2), "target": m.group(3)}

        elif content.startswith("REDUCE"):
            m = re.match(r"REDUCE\s+(\w+)\s+WITH\s+(.+?)\s+→\s+(\w+)", content)
            if m:
                return {"type": "reduce", "source": m.group(1), "expression": m.group(2), "target": m.group(3)}

        # === ERROR HANDLING ===
        elif content.startswith("TRY"):
            return {"type": "try"}

        elif content.startswith("CATCH"):
            m = re.match(r"CATCH\s+(\w+)", content)
            error_var = m.group(1) if m else "error"
            return {"type": "catch", "error_var": error_var}

        elif content.startswith("END TRY"):
            return {"type": "endtry"}

        # === FUNCTIONS ===
        elif content.startswith("CALL"):
            m = re.match(r"CALL\s+(\w+)\((.*?)\)\s*(?:→\s*(\w+))?", content)
            if m:
                args = [a.strip() for a in m.group(2).split(",")] if m.group(2) else []
                return {"type": "call", "func_name": m.group(1), "args": args, "result": m.group(3)}

        # === OOP ===
        elif content.startswith("CREATE"):
            m = re.match(r"CREATE\s+(\w+)\s+←\s+(\w+)\((.*?)\)", content)
            if m:
                args = [a.strip() for a in m.group(3).split(",")] if m.group(3) else []
                return {"type": "create_instance", "var": m.group(1), "class_name": m.group(2), "args": args}

        # === AI PIPELINE ===
        elif content.startswith("LOAD_MODEL"):
            m = re.match(r"LOAD_MODEL\s+[\"'](.+?)[\"']\s*(?:→\s*(\w+))?", content)
            if m:
                return {"type": "load_model", "model_name": m.group(1), "var": m.group(2) or "model"}

        elif content.startswith("PREDICT"):
            m = re.match(r"PREDICT\s+(.+?)\s+→\s+(\w+)", content)
            if m:
                return {"type": "predict", "input": m.group(1), "output": m.group(2)}

        elif content.startswith("TRAIN"):
            m = re.match(r"TRAIN\s+(\w+)\s+ON\s+(.+)", content)
            if m:
                return {"type": "train", "model": m.group(1), "data": m.group(2)}

        else:
            return {"type": "raw", "code": content}

class ExplainAICompiler:
    def __init__(self, ast):
        self.ast = ast
        self.code = []
        self.indent = "    "
        self.level = 0
        self.libs = set()

    def compile(self):
        fn = self.ast["function_name"]
        args = ", ".join(self.ast["inputs"])
        self.code.append(f"def {fn}({args}):")
        self.level += 1

        for stmt in self.ast["body"]:
            self._emit(stmt)

        return "\n".join(sorted(self.libs)) + "\n\n" + "\n".join(self.code)

    def _emit(self, stmt):
        indent = self.indent * self.level

        # === ASSIGNMENT ===
        if stmt["type"] == "assign":
            self.code.append(f"{indent}{stmt['target']} = {stmt['value']}")

        # === IMPORTS ===
        elif stmt["type"] == "import":
            self.libs.add(f"import {stmt['lib']}")
            self._try_import(stmt['lib'])

        elif stmt["type"] == "apikey":
            self.code.append(f"{indent}api_key = '{stmt['value']}'")

        # === CONTROL FLOW ===
        elif stmt["type"] == "for":
            self.code.append(f"{indent}for {stmt['var']} in range({stmt['start']}, {stmt['end']}+1):")
            self.level += 1

        elif stmt["type"] == "foreach":
            self.code.append(f"{indent}for {stmt['var']} in {stmt['iterable']}:")
            self.level += 1

        elif stmt["type"] == "endfor" or stmt["type"] == "endforeach":
            self.level -= 1

        elif stmt["type"] == "while":
            self.code.append(f"{indent}while {stmt['condition']}:")
            self.level += 1

        elif stmt["type"] == "endwhile":
            self.level -= 1

        elif stmt["type"] == "if":
            self.code.append(f"{indent}if {stmt['condition']}:")
            self.level += 1

        elif stmt["type"] == "else":
            self.level -= 1
            indent = self.indent * self.level
            self.code.append(f"{indent}else:")
            self.level += 1

        elif stmt["type"] == "endif":
            self.level -= 1

        elif stmt["type"] == "print":
            self.code.append(f"{indent}print({stmt['value']})")

        elif stmt["type"] == "return":
            self.code.append(f"{indent}return {stmt['value']}")

        elif stmt["type"] == "break":
            self.code.append(f"{indent}break")

        elif stmt["type"] == "continue":
            self.code.append(f"{indent}continue")

        elif stmt["type"] == "comment":
            self.code.append(f"{indent}# {stmt['text']}")

        # === DATA STRUCTURES ===
        elif stmt["type"] == "list_create":
            self.code.append(f"{indent}{stmt['name']} = {stmt['value']}")

        elif stmt["type"] == "dict_create":
            self.code.append(f"{indent}{stmt['name']} = {stmt['value']}")

        elif stmt["type"] == "list_append":
            self.code.append(f"{indent}{stmt['list_name']}.append({stmt['value']})")

        elif stmt["type"] == "list_remove":
            self.code.append(f"{indent}{stmt['list_name']}.remove({stmt['value']})")

        elif stmt["type"] == "get_value":
            self.code.append(f"{indent}{stmt['target']} = {stmt['source']}")

        # === UTILITIES ===
        elif stmt["type"] == "sort":
            self.code.append(f"{indent}{stmt['target']} = sorted({stmt['source']})")

        elif stmt["type"] == "filter":
            cond = stmt['condition'].replace('x', '_x')
            self.code.append(f"{indent}{stmt['target']} = [_x for _x in {stmt['source']} if {cond}]")

        elif stmt["type"] == "map":
            expr = stmt['expression'].replace('x', '_x')
            self.code.append(f"{indent}{stmt['target']} = [{expr} for _x in {stmt['source']}]")

        elif stmt["type"] == "reduce":
            self.libs.add("from functools import reduce")
            self.code.append(f"{indent}{stmt['target']} = reduce(lambda acc, x: {stmt['expression']}, {stmt['source']})")

        # === ERROR HANDLING ===
        elif stmt["type"] == "try":
            self.code.append(f"{indent}try:")
            self.level += 1

        elif stmt["type"] == "catch":
            self.level -= 1
            indent = self.indent * self.level
            self.code.append(f"{indent}except Exception as {stmt['error_var']}:")
            self.level += 1

        elif stmt["type"] == "endtry":
            self.level -= 1

        # === FUNCTIONS ===
        elif stmt["type"] == "call":
            args_str = ", ".join(stmt['args'])
            if stmt.get('result'):
                self.code.append(f"{indent}{stmt['result']} = {stmt['func_name']}({args_str})")
            else:
                self.code.append(f"{indent}{stmt['func_name']}({args_str})")

        # === OOP ===
        elif stmt["type"] == "create_instance":
            args_str = ", ".join(stmt['args']) if stmt['args'] else ""
            self.code.append(f"{indent}{stmt['var']} = {stmt['class_name']}({args_str})")

        # === AI PIPELINE ===
        elif stmt["type"] == "load_model":
            self.libs.add("from transformers import pipeline")
            self.code.append(f"{indent}{stmt['var']} = pipeline('{stmt['model_name']}')")

        elif stmt["type"] == "predict":
            self.code.append(f"{indent}{stmt['output']} = model({stmt['input']})")

        elif stmt["type"] == "train":
            self.code.append(f"{indent}# Training {stmt['model']} on {stmt['data']}")
            self.code.append(f"{indent}{stmt['model']}.fit({stmt['data']})")

        elif stmt["type"] == "raw":
            self.code.append(f"{indent}{stmt['code']}")

    def _try_import(self, module):
        try:
            importlib.import_module(module)
        except ImportError:
            os.system(f"pip install {module}")

# ------------------------------
# Runner
# ------------------------------

def run_explainai(filename, save_python=False, verbose=False):
    if not filename.endswith(".eai") and not filename.endswith(".epd"):
        raise ValueError("Only .eai or .epd files are supported.")
    if not os.path.exists(filename):
        raise FileNotFoundError(f"{filename} does not exist.")

    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    parser = ExplainAIParser()
    ast_tree = parser.parse(lines)

    compiler = ExplainAICompiler(ast_tree)
    py_code = compiler.compile()

    if verbose:
        print("\n🔧 Generated Python Code:\n")
        print(py_code)

    if save_python:
        py_filename = os.path.splitext(os.path.basename(filename))[0] + "_compiled.py"
        with open(py_filename, "w", encoding="utf-8") as f:
            f.write(py_code)
        print(f"💾 Python source saved to {py_filename}")

    print(f"\n📥 Enter values for: {', '.join(ast_tree['inputs'])}")
    user_inputs = []
    for var in ast_tree['inputs']:
        val = input(f"→ {var} = ")
        try:
            user_inputs.append(ast.literal_eval(val))
        except:
            user_inputs.append(val)

    exec_globals = {}
    print("\n🚀 Running...\n")
    exec(py_code, exec_globals)
    result = exec_globals[ast_tree["function_name"]](*user_inputs)
    print("\n✅ Output:", result)

# ------------------------------
# Entry Point
# ------------------------------

def main():
    parser = argparse.ArgumentParser(description="ExplainCode 2.0 Compiler & Runner")
    parser.add_argument("filename", help="The .eai or .epd file to run")
    parser.add_argument("-s", "--save", action="store_true", help="Save the generated Python code to a file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print the generated Python code")
    
    args = parser.parse_args()

    try:
        run_explainai(args.filename, save_python=args.save, verbose=args.verbose)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
