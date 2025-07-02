import re
import sys
import os
import ast

class ExplainCodeCompiler:
    def __init__(self):
        self.indent = "    "
        self.current_indent = ""
        self.function_name = ""
        self.inputs = []

    def compile(self, lines):
        self.current_indent = ""
        code = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("ALGORITHM"):
                self.function_name = line.split()[1]

            elif line.startswith("INPUT:"):
                self.inputs = [x.strip() for x in line.replace("INPUT:", "").split(",")]
                param_list = ", ".join(self.inputs)
                code.append(f"def {self.function_name}({param_list}):")
                self.current_indent = self.indent

            elif line.startswith("OUTPUT:"):
                continue  # No need to use OUTPUT in Python

            elif line.startswith("STEP"):
                code.append(self.current_indent + f"# {line}")

            elif line.startswith("Set"):
                match = re.match(r"Set (.+?) ← (.+)", line)
                if match:
                    left, right = match.groups()
                    code.append(self.current_indent + f"{left.strip()} = {right.strip()}")

            elif line.startswith("IF"):
                condition = line[3:].replace("THEN", "").strip()
                condition = self._convert_bool(condition)
                code.append(self.current_indent + f"if {condition}:")
                self.current_indent += self.indent

            elif line.startswith("END IF"):
                self.current_indent = self.current_indent[:-len(self.indent)]

            elif line.startswith("FOR"):
                match = re.match(r"FOR (.+?) ← (.+?) to (.+?) DO", line)
                if match:
                    var, start, end = match.groups()
                    code.append(self.current_indent + f"for {var.strip()} in range({start.strip()}, {end.strip()} + 1):")
                    self.current_indent += self.indent

            elif line.startswith("END FOR"):
                self.current_indent = self.current_indent[:-len(self.indent)]

            elif line.startswith("WHILE"):
                condition = line.replace("WHILE", "").replace("DO", "").strip()
                condition = self._convert_bool(condition)
                code.append(self.current_indent + f"while {condition}:")
                self.current_indent += self.indent

            elif line.startswith("END WHILE"):
                self.current_indent = self.current_indent[:-len(self.indent)]

            elif line.startswith("BREAK"):
                code.append(self.current_indent + "break")

            elif line.startswith("PRINT"):
                expr = line.replace("PRINT", "").strip()
                code.append(self.current_indent + f"print({expr})")

            elif line.startswith("RETURN"):
                value = line.replace("RETURN", "").strip()
                code.append(self.current_indent + f"return {value}")

            elif line.startswith("END ALGORITHM"):
                break

            else:
                raise SyntaxError(f"Unknown instruction: {line}")

        return "\n".join(code), self.function_name, self.inputs

    def _convert_bool(self, condition):
        return condition.replace("AND", "and").replace("OR", "or").replace("NOT", "not")

    def compile_and_run(self, filename):
        if not filename.endswith(".epd"):
            raise ValueError("Only .epd files are supported.")
        if not os.path.exists(filename):
            raise FileNotFoundError("The file does not exist.")

        with open(filename, "r") as f:
            lines = f.readlines()

        py_code, func_name, inputs = self.compile(lines)

        exec_globals = {}
        compiled_code = py_code + f"\n\n# Call the function with user inputs\n"

        user_args = []
        print(f"\n📥 Enter values for: {', '.join(inputs)}")
        for var in inputs:
            raw = input(f"→ {var} = ")
            try:
                val = ast.literal_eval(raw)  # Handles lists, ints, strings safely
            except:
                val = raw
            user_args.append(val)

        call_expr = f"{func_name}({', '.join(repr(arg) for arg in user_args)})"
        compiled_code += f"result = {call_expr}\nprint('✅ Output:', result)\n"

        print("\n🧠 Compiled Python Code:\n")
        print(py_code)

        print("\n🚀 Running...\n")
        exec(compiled_code, exec_globals)

# ---------- Main ----------
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python explaincode_compiler.py <file.epd>")
        sys.exit(1)

    source_file = sys.argv[1]
    compiler = ExplainCodeCompiler()
    compiler.compile_and_run(source_file)
