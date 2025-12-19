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

        # === ASSIGNMENT ===
        if content.startswith("Set"):
            m = re.match(r"Set\s+(.+?)\s+←\s+(.+)", content)
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
        try_stack = []  # For TRY/CATCH handling
        
        while i < len(body):
            stmt = body[i]
            t = stmt['type']
            
            try:
                # === ASSIGNMENT ===
                if t == 'assign':
                    self.env[stmt['target']] = eval(stmt['value'], {}, self.env)
                
                # === IMPORTS ===
                elif t == 'import':
                    self._try_import(stmt['lib'])
                elif t == 'apikey':
                    self.env['api_key'] = stmt['value']
                
                # === OUTPUT ===
                elif t == 'print':
                    self.output(str(eval(stmt['value'], {}, self.env)))
                elif t == 'return':
                    return eval(stmt['value'], {}, self.env)
                elif t == 'raw':
                    exec(stmt['code'], {}, self.env)
                
                # === CONDITIONALS ===
                elif t == 'if':
                    cond = eval(stmt['condition'], {}, self.env)
                    if not cond:
                        skip = 1
                        while skip and i < len(body):
                            i += 1
                            if body[i]['type'] in ('else', 'endif'):
                                skip -= 1
                                break
                        continue
                elif t == 'else':
                    while i < len(body) and body[i]['type'] != 'endif':
                        i += 1
                elif t == 'endif':
                    pass
                
                # === FOR LOOP ===
                elif t == 'for':
                    loop_var = stmt['var']
                    loop_start = int(eval(stmt['start'], {}, self.env))
                    loop_end = int(eval(stmt['end'], {}, self.env)) + 1
                    stack.append(('for', i, loop_var, loop_end))
                    self.env[loop_var] = loop_start
                elif t == 'endfor':
                    _, i_start, loop_var, loop_end = stack[-1]
                    self.env[loop_var] += 1
                    if self.env[loop_var] < loop_end:
                        i = i_start
                        continue
                    else:
                        stack.pop()
                
                # === FOREACH LOOP ===
                elif t == 'foreach':
                    iterable = eval(stmt['iterable'], {}, self.env)
                    iterator = iter(iterable)
                    try:
                        self.env[stmt['var']] = next(iterator)
                        stack.append(('foreach', i, stmt['var'], iterator))
                    except StopIteration:
                        # Empty iterable, skip to end
                        while i < len(body) and body[i]['type'] != 'endforeach':
                            i += 1
                elif t == 'endforeach':
                    _, i_start, loop_var, iterator = stack[-1]
                    try:
                        self.env[loop_var] = next(iterator)
                        i = i_start
                        continue
                    except StopIteration:
                        stack.pop()
                
                # === WHILE LOOP ===
                elif t == 'while':
                    cond = eval(stmt['condition'], {}, self.env)
                    if cond:
                        stack.append(('while', i))
                    else:
                        while i < len(body) and body[i]['type'] != 'endwhile':
                            i += 1
                elif t == 'endwhile':
                    i = stack[-1][1] - 1
                    stack.pop()
                
                # === BREAK/CONTINUE ===
                elif t == 'break':
                    while i < len(body) and body[i]['type'] not in ('endwhile', 'endfor', 'endforeach'):
                        i += 1
                    if stack:
                        stack.pop()
                elif t == 'continue':
                    if stack:
                        loop_type = stack[-1][0]
                        if loop_type == 'for':
                            while i < len(body) and body[i]['type'] != 'endfor':
                                i += 1
                            i -= 1  # Will be incremented
                        elif loop_type == 'foreach':
                            while i < len(body) and body[i]['type'] != 'endforeach':
                                i += 1
                            i -= 1
                        elif loop_type == 'while':
                            while i < len(body) and body[i]['type'] != 'endwhile':
                                i += 1
                            i -= 1
                
                # === DATA STRUCTURES ===
                elif t == 'list_create':
                    self.env[stmt['name']] = eval(stmt['value'], {}, self.env)
                elif t == 'dict_create':
                    self.env[stmt['name']] = eval(stmt['value'], {}, self.env)
                elif t == 'list_append':
                    self.env[stmt['list_name']].append(eval(stmt['value'], {}, self.env))
                elif t == 'list_remove':
                    self.env[stmt['list_name']].remove(eval(stmt['value'], {}, self.env))
                elif t == 'get_value':
                    self.env[stmt['target']] = eval(stmt['source'], {}, self.env)
                
                # === UTILITIES ===
                elif t == 'sort':
                    self.env[stmt['target']] = sorted(self.env[stmt['source']])
                elif t == 'filter':
                    source = self.env[stmt['source']]
                    cond = stmt['condition']
                    self.env[stmt['target']] = [x for x in source if eval(cond.replace('x', str(x)), {}, self.env)]
                elif t == 'map':
                    source = self.env[stmt['source']]
                    expr = stmt['expression']
                    self.env[stmt['target']] = [eval(expr.replace('x', str(x)), {}, self.env) for x in source]
                elif t == 'reduce':
                    from functools import reduce
                    source = self.env[stmt['source']]
                    expr = stmt['expression']
                    self.env[stmt['target']] = reduce(lambda acc, x: eval(expr, {'acc': acc, 'x': x}, {}), source)
                
                # === ERROR HANDLING ===
                elif t == 'try':
                    try_stack.append(i)
                elif t == 'catch':
                    # If we reach catch normally (no error), skip to END TRY
                    while i < len(body) and body[i]['type'] != 'endtry':
                        i += 1
                elif t == 'endtry':
                    if try_stack:
                        try_stack.pop()
                
                # === FUNCTIONS ===
                elif t == 'call':
                    func = self.env.get(stmt['func_name'])
                    if callable(func):
                        args = [eval(a, {}, self.env) for a in stmt['args']] if stmt['args'] else []
                        result = func(*args)
                        if stmt.get('result'):
                            self.env[stmt['result']] = result
                
                # === OOP ===
                elif t == 'create_instance':
                    cls = self.env.get(stmt['class_name'])
                    if cls:
                        args = [eval(a, {}, self.env) for a in stmt['args']] if stmt['args'] else []
                        self.env[stmt['var']] = cls(*args)
                
                # === AI PIPELINE ===
                elif t == 'load_model':
                    try:
                        from transformers import pipeline
                        self.env[stmt['var']] = pipeline(stmt['model_name'])
                    except ImportError:
                        os.system("pip install transformers")
                        from transformers import pipeline
                        self.env[stmt['var']] = pipeline(stmt['model_name'])
                elif t == 'predict':
                    model = self.env.get('model')
                    if model:
                        inp = eval(stmt['input'], {}, self.env)
                        self.env[stmt['output']] = model(inp)
                elif t == 'train':
                    model = self.env.get(stmt['model'])
                    if model and hasattr(model, 'fit'):
                        data = eval(stmt['data'], {}, self.env)
                        model.fit(data)
                
            except Exception as e:
                # Handle errors in TRY blocks
                if try_stack:
                    # Find the CATCH block
                    while i < len(body) and body[i]['type'] != 'catch':
                        i += 1
                    if i < len(body):
                        self.env[body[i].get('error_var', 'error')] = str(e)
                else:
                    raise e
            
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

def main():
    app = QApplication(sys.argv)
    window = ExplainCodeApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
