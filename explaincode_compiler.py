# explainai_compiler.py

import re
import sys
import os
import ast
import importlib

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

        if content.startswith("Set"):
            m = re.match(r"Set\s+(.+?)\s+←\s+(.+)", content)
            if m:
                return {"type": "assign", "target": m.group(1), "value": m.group(2)}

        elif content.startswith("Import"):
            return {"type": "import", "lib": content.split()[1]}

        elif content.startswith("KEY:"):
            return {"type": "apikey", "value": content.replace("KEY:", "").strip()}

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

        if stmt["type"] == "assign":
            self.code.append(f"{indent}{stmt['target']} = {stmt['value']}")

        elif stmt["type"] == "import":
            self.libs.add(f"import {stmt['lib']}")
            self._try_import(stmt['lib'])

        elif stmt["type"] == "apikey":
            self.code.append(f"{indent}api_key = '{stmt['value']}'")

        elif stmt["type"] == "for":
            self.code.append(f"{indent}for {stmt['var']} in range({stmt['start']}, {stmt['end']}+1):")
            self.level += 1

        elif stmt["type"] == "endfor":
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

        elif stmt["type"] == "comment":
            self.code.append(f"{indent}# {stmt['text']}")

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

def run_explainai(filename):
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

    print("\n🔧 Generated Python Code:\n")
    print(py_code)

    py_filename = os.path.splitext(os.path.basename(filename))[0] + "_compiled.py"
    with open(py_filename, "w", encoding="utf-8") as f:
        f.write(py_code)

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

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python explainai_compiler.py <file.eai|file.epd>")
        sys.exit(1)

    run_explainai(sys.argv[1])
