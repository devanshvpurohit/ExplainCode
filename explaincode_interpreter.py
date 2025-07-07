import sys
import os
import re
import ast
import importlib
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTextEdit, QPushButton,
    QVBoxLayout, QFileDialog, QLabel, QMessageBox, QInputDialog
)


class ExplainCodeParser:
    def __init__(self):
        self.ast = {
            "function_name": "",
            "inputs": [],
            "body": []
        }

    def parse(self, lines):
        lines = [line.strip() for line in lines if line.strip()]
        if not lines[0].startswith(("ALGORITHM", "MODEL", "API_CALL")):
            raise SyntaxError("File must start with ALGORITHM, MODEL, or API_CALL.")
        self.ast["function_name"] = lines[0].split()[1]
        for line in lines[1:]:
            if line.startswith("INPUT:"):
                self.ast["inputs"] = [x.strip() for x in line.replace("INPUT:", "").split(",")]
            elif line.startswith("OUTPUT:"):
                continue
            elif line.startswith(("END ALGORITHM", "END MODEL", "END API_CALL")):
                break
            elif line.startswith("STEP"):
                step = self._parse_step(line)
                if step:
                    self.ast["body"].append(step)
        return self.ast

    def _parse_step(self, line):
        match = re.match(r"STEP\s+\d+:?\s*(.+)", line)
        if not match: return None
        content = match.group(1)

        if content.startswith("Set"):
            m = re.match(r"Set\s+(.+?)\s+←\s+(.+)", content)
            return {"type": "assign", "target": m.group(1), "value": m.group(2)}
        elif content.startswith("Import"):
            return {"type": "import", "lib": content.split()[1]}
        elif content.startswith("KEY:"):
            return {"type": "apikey", "value": content.replace("KEY:", "").strip()}
        elif content.startswith("FOR"):
            m = re.match(r"FOR\s+(\w+)\s+←\s+(\d+)\s+to\s+(.+?)\s+DO", content)
            if m:
                return {"type": "for", "var": m.group(1), "start": m.group(2), "end": m.group(3)}
        elif content.startswith("WHILE"):
            return {"type": "while", "condition": content.replace("WHILE", "").replace("DO", "").strip()}
        elif content.startswith("IF"):
            return {"type": "if", "condition": content.replace("IF", "").replace("THEN", "").strip()}
        elif content.startswith("ELSE"):
            return {"type": "else"}
        elif content.startswith("END IF"):
            return {"type": "endif"}
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


class ExplainCodeInterpreter:
    def __init__(self, ast, gui_print_fn=None, gui_input_fn=None):
        self.ast = ast
        self.env = {}
        self.output = gui_print_fn or print
        self.input_dialog = gui_input_fn or input

    def run(self):
        for var in self.ast['inputs']:
            val, ok = self.input_dialog(f"→ {var} =")
            if not ok: return None
            try:
                self.env[var] = ast.literal_eval(val)
            except:
                self.env[var] = val
        return self._execute_body(self.ast['body'])

    def _execute_body(self, body):
        i = 0
        stack = []
        while i < len(body):
            stmt = body[i]
            t = stmt['type']
            if t == 'assign':
                self.env[stmt['target']] = eval(stmt['value'], {}, self.env)
            elif t == 'import':
                self._try_import(stmt['lib'])
            elif t == 'apikey':
                self.env['api_key'] = stmt['value']
            elif t == 'print':
                self.output(str(eval(stmt['value'], {}, self.env)))
            elif t == 'return':
                return eval(stmt['value'], {}, self.env)
            elif t == 'raw':
                exec(stmt['code'], {}, self.env)
            elif t == 'if':
                cond = eval(stmt['condition'], {}, self.env)
                if not cond:
                    # skip to ELSE or END IF
                    skip = 1
                    while skip and i < len(body):
                        i += 1
                        if body[i]['type'] in ('else', 'endif'):
                            skip -= 1
                            break
                    continue
            elif t == 'else':
                # skip to END IF
                while i < len(body) and body[i]['type'] != 'endif':
                    i += 1
            elif t == 'for':
                loop_var = stmt['var']
                loop_start = int(eval(stmt['start'], {}, self.env))
                loop_end = int(eval(stmt['end'], {}, self.env)) + 1
                stack.append((i, loop_var, loop_end))
                self.env[loop_var] = loop_start
            elif t == 'endfor':
                i_start, loop_var, loop_end = stack[-1]
                self.env[loop_var] += 1
                if self.env[loop_var] < loop_end:
                    i = i_start
                    continue
                else:
                    stack.pop()
            elif t == 'while':
                cond = eval(stmt['condition'], {}, self.env)
                if cond:
                    stack.append(i)
                else:
                    while i < len(body) and body[i]['type'] != 'endwhile':
                        i += 1
            elif t == 'endwhile':
                i = stack[-1] - 1
                stack.pop()
            elif t == 'break':
                while i < len(body) and body[i]['type'] not in ('endwhile', 'endfor'):
                    i += 1
            i += 1

    def _try_import(self, module):
        mod_name = module.split('.')[0]
        try:
            mod = importlib.import_module(module)
        except ImportError:
            os.system(f"pip install {mod_name}")
            mod = importlib.import_module(module)
        self.env[mod_name] = mod


class ExplainCodeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ExplainCode IDE (PyQt5)")
        self.setGeometry(200, 200, 900, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.editor = QTextEdit()
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.status = QLabel("🔹 Ready")

        load_btn = QPushButton("📂 Open File")
        run_btn = QPushButton("▶️ Run Code")

        load_btn.clicked.connect(self.load_file)
        run_btn.clicked.connect(self.run_code)

        layout.addWidget(self.editor)
        layout.addWidget(load_btn)
        layout.addWidget(run_btn)
        layout.addWidget(QLabel("🧠 Output:"))
        layout.addWidget(self.output)
        layout.addWidget(self.status)

        self.setLayout(layout)

    def gui_input(self, prompt):
        val, ok = QInputDialog.getText(self, "Input Required", prompt)
        return val, ok

    def gui_print(self, text):
        self.output.append(text)

    def load_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open ExplainCode", "", "ExplainCode Files (*.epd *.eai)")
        if path:
            with open(path, "r", encoding="utf-8") as f:
                self.editor.setText(f.read())
            self.status.setText(f"📄 Loaded: {os.path.basename(path)}")

    def run_code(self):
        self.output.clear()
        code = self.editor.toPlainText().splitlines()
        try:
            parser = ExplainCodeParser()
            ast_tree = parser.parse(code)
            interpreter = ExplainCodeInterpreter(ast_tree, self.gui_print, self.gui_input)
            result = interpreter.run()
            if result is not None:
                self.output.append(f"\n✅ Output: {result}")
            self.status.setText("✅ Executed successfully.")
        except Exception as e:
            self.output.append(f"\n❌ Error: {str(e)}")
            self.status.setText("❌ Execution failed.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExplainCodeApp()
    window.show()
    sys.exit(app.exec_())
