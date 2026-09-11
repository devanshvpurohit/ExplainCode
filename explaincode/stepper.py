"""
explaincode.stepper

Step-by-step execution and state-tracing engine.
Extends the ExplainCode interpreter architecture with granular statement-by-statement
execution, variable state tracking, condition resolution, and state resets.
"""

import ast
import copy
from typing import Dict, Any, List, Optional, Tuple, Callable


class StepperState:
    """Snapshot of execution state after a single step."""

    def __init__(
        self,
        step_index: int,
        total_steps: int,
        statement: Optional[Dict[str, Any]],
        statement_text: str,
        env: Dict[str, Any],
        changed_vars: Dict[str, Any],
        condition_info: Optional[Dict[str, Any]] = None,
        loop_info: Optional[Dict[str, Any]] = None,
        output_emitted: Optional[str] = None,
        return_value: Any = None,
        is_finished: bool = False,
        error: Optional[str] = None
    ):
        self.step_index = step_index
        self.total_steps = total_steps
        self.statement = statement
        self.statement_text = statement_text
        self.env = env
        self.changed_vars = changed_vars
        self.condition_info = condition_info
        self.loop_info = loop_info
        self.output_emitted = output_emitted
        self.return_value = return_value
        self.is_finished = is_finished
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_index": self.step_index,
            "total_steps": self.total_steps,
            "statement_text": self.statement_text,
            "variables": {k: repr(v) for k, v in self.env.items() if not k.startswith("__") and not callable(v)},
            "changed_vars": {k: repr(v) for k, v in self.changed_vars.items()},
            "condition_info": self.condition_info,
            "loop_info": self.loop_info,
            "output_emitted": self.output_emitted,
            "return_value": repr(self.return_value) if self.return_value is not None else None,
            "is_finished": self.is_finished,
            "error": self.error
        }


class ExplainCodeStepper:
    """
    Non-blocking, step-by-step execution tracer for ExplainCode AST.
    Maintains program environment, execution stack, and history.
    """

    def __init__(self, ast_tree: Dict[str, Any], initial_inputs: Optional[Dict[str, Any]] = None):
        self.ast = ast_tree
        self.initial_inputs = initial_inputs or {}
        self.body: List[Dict[str, Any]] = self.ast.get("body", [])
        self.total_steps = len(self.body)
        self.output_log: List[str] = []
        self.reset()

    def reset(self):
        """Resets execution state back to the beginning."""
        self.pc = 0  # Program counter / statement index in body
        self.env: Dict[str, Any] = {}
        # Apply initial inputs
        for k, v in self.initial_inputs.items():
            self.env[k] = copy.deepcopy(v)

        self.stack: List[Tuple[Any, ...]] = []
        self.try_stack: List[int] = []
        self.history: List[StepperState] = []
        self.is_finished = False
        self.return_value = None
        self.error: Optional[str] = None
        self.output_log.clear()

    def set_input(self, var_name: str, value: Any):
        """Sets or overrides an input variable."""
        self.initial_inputs[var_name] = value
        self.env[var_name] = value

    def is_done(self) -> bool:
        return self.is_finished or self.pc >= len(self.body)

    def _stmt_to_text(self, stmt: Dict[str, Any]) -> str:
        """Converts an AST statement node into readable ExplainCode syntax."""
        t = stmt.get("type", "")
        if t == "assign":
            return f"SET {stmt.get('target')} ← {stmt.get('value')}"
        elif t == "print":
            return f"PRINT {stmt.get('value')}"
        elif t == "if":
            return f"IF {stmt.get('condition')} THEN"
        elif t == "else":
            return "ELSE"
        elif t == "endif":
            return "END IF"
        elif t == "for":
            return f"FOR {stmt.get('var')} ← {stmt.get('start')} to {stmt.get('end')} DO"
        elif t == "endfor":
            return "END FOR"
        elif t == "foreach":
            return f"FOREACH {stmt.get('var')} IN {stmt.get('iterable')} DO"
        elif t == "endforeach":
            return "END FOREACH"
        elif t == "while":
            return f"WHILE {stmt.get('condition')} DO"
        elif t == "endwhile":
            return "END WHILE"
        elif t == "break":
            return "BREAK"
        elif t == "continue":
            return "CONTINUE"
        elif t == "return":
            return f"RETURN {stmt.get('value')}"
        elif t == "list_create":
            return f"LIST {stmt.get('name')} ← {stmt.get('value')}"
        elif t == "dict_create":
            return f"DICT {stmt.get('name')} ← {stmt.get('value')}"
        elif t == "list_append":
            return f"APPEND {stmt.get('list_name')} ← {stmt.get('value')}"
        elif t == "list_remove":
            return f"REMOVE {stmt.get('list_name')} ← {stmt.get('value')}"
        elif t == "get_value":
            return f"GET {stmt.get('source')} → {stmt.get('target')}"
        elif t == "sort":
            return f"SORT {stmt.get('source')} → {stmt.get('target')}"
        elif t == "filter":
            return f"FILTER {stmt.get('source')} WHERE {stmt.get('condition')} → {stmt.get('target')}"
        elif t == "map":
            return f"MAP {stmt.get('source')} WITH {stmt.get('expression')} → {stmt.get('target')}"
        elif t == "reduce":
            return f"REDUCE {stmt.get('source')} WITH {stmt.get('expression')} → {stmt.get('target')}"
        elif t == "try":
            return "TRY"
        elif t == "catch":
            return f"CATCH {stmt.get('error_var', 'error')}"
        elif t == "endtry":
            return "END TRY"
        elif t == "call":
            args = ", ".join(stmt.get('args', []))
            res = f" → {stmt['result']}" if stmt.get('result') else ""
            return f"CALL {stmt.get('func_name')}({args}){res}"
        elif t == "raw":
            return str(stmt.get("code", ""))
        return str(stmt)

    def step(self) -> StepperState:
        """
        Executes exactly one statement from the body.
        Returns a StepperState recording all state changes.
        """
        if self.is_done():
            state = StepperState(
                step_index=self.pc,
                total_steps=self.total_steps,
                statement=None,
                statement_text="[Execution Finished]",
                env=copy.copy(self.env),
                changed_vars={},
                return_value=self.return_value,
                is_finished=True,
                error=self.error
            )
            return state

        curr_i = self.pc
        stmt = self.body[curr_i]
        t = stmt.get("type")
        stmt_text = self._stmt_to_text(stmt)

        env_before = copy.copy(self.env)
        condition_info = None
        loop_info = None
        output_emitted = None

        try:
            # === ASSIGNMENT ===
            if t == "assign":
                val = eval(stmt["value"], {}, self.env)
                self.env[stmt["target"]] = val
                self.pc += 1

            # === PRINT / OUTPUT ===
            elif t == "print":
                val = eval(stmt["value"], {}, self.env)
                output_str = str(val)
                self.output_log.append(output_str)
                output_emitted = output_str
                self.pc += 1

            # === RETURN ===
            elif t == "return":
                val = eval(stmt["value"], {}, self.env)
                self.return_value = val
                self.is_finished = True
                self.pc = len(self.body)

            # === RAW PYTHON CODE ===
            elif t == "raw":
                exec(stmt["code"], {}, self.env)
                self.pc += 1

            # === CONDITIONALS ===
            elif t == "if":
                cond = bool(eval(stmt["condition"], {}, self.env))
                condition_info = {
                    "condition": stmt["condition"],
                    "result": cond,
                    "branch_taken": "THEN branch" if cond else "Skipping to ELSE / END IF"
                }
                if cond:
                    self.pc += 1
                else:
                    # Skip to matching else or endif
                    skip = 1
                    i = curr_i + 1
                    while skip > 0 and i < len(self.body):
                        if self.body[i]["type"] == "if":
                            skip += 1
                        elif self.body[i]["type"] in ("else", "endif"):
                            skip -= 1
                            if skip == 0:
                                self.pc = i + 1 if self.body[i]["type"] == "else" else i + 1
                                break
                        i += 1
                    else:
                        self.pc = i

            elif t == "else":
                # If we hit else sequentially, the IF branch was taken, so skip to endif
                skip = 1
                i = curr_i + 1
                while skip > 0 and i < len(self.body):
                    if self.body[i]["type"] == "if":
                        skip += 1
                    elif self.body[i]["type"] == "endif":
                        skip -= 1
                        if skip == 0:
                            self.pc = i + 1
                            break
                    i += 1
                else:
                    self.pc = i

            elif t == "endif":
                self.pc += 1

            # === FOR LOOP ===
            elif t == "for":
                loop_var = stmt["var"]
                start = int(eval(str(stmt["start"]), {}, self.env))
                end = int(eval(str(stmt["end"]), {}, self.env))
                self.env[loop_var] = start
                self.stack.append(("for", curr_i, loop_var, end + 1))
                loop_info = {
                    "loop_type": "FOR",
                    "variable": loop_var,
                    "current_value": start,
                    "target_range": f"{start} to {end}"
                }
                self.pc += 1

            elif t == "endfor":
                if self.stack and self.stack[-1][0] == "for":
                    _, i_start, loop_var, loop_end = self.stack[-1]
                    self.env[loop_var] += 1
                    curr_val = self.env[loop_var]
                    if curr_val < loop_end:
                        loop_info = {
                            "loop_type": "FOR",
                            "variable": loop_var,
                            "current_value": curr_val,
                            "continuing": True
                        }
                        self.pc = i_start + 1
                    else:
                        self.stack.pop()
                        loop_info = {
                            "loop_type": "FOR",
                            "variable": loop_var,
                            "completed": True
                        }
                        self.pc += 1
                else:
                    self.pc += 1

            # === FOREACH LOOP ===
            elif t == "foreach":
                iterable = eval(stmt["iterable"], {}, self.env)
                iterator = iter(iterable)
                try:
                    first_val = next(iterator)
                    self.env[stmt["var"]] = first_val
                    self.stack.append(("foreach", curr_i, stmt["var"], iterator))
                    loop_info = {
                        "loop_type": "FOREACH",
                        "variable": stmt["var"],
                        "current_value": first_val
                    }
                    self.pc += 1
                except StopIteration:
                    # Empty iterable: skip to endforeach
                    i = curr_i + 1
                    while i < len(self.body) and self.body[i]["type"] != "endforeach":
                        i += 1
                    self.pc = i + 1

            elif t == "endforeach":
                if self.stack and self.stack[-1][0] == "foreach":
                    _, i_start, loop_var, iterator = self.stack[-1]
                    try:
                        next_val = next(iterator)
                        self.env[loop_var] = next_val
                        loop_info = {
                            "loop_type": "FOREACH",
                            "variable": loop_var,
                            "current_value": next_val,
                            "continuing": True
                        }
                        self.pc = i_start + 1
                    except StopIteration:
                        self.stack.pop()
                        loop_info = {"loop_type": "FOREACH", "completed": True}
                        self.pc += 1
                else:
                    self.pc += 1

            # === WHILE LOOP ===
            elif t == "while":
                cond = bool(eval(stmt["condition"], {}, self.env))
                condition_info = {
                    "condition": stmt["condition"],
                    "result": cond,
                    "branch_taken": "Entering loop body" if cond else "Condition False: exiting loop"
                }
                if cond:
                    self.stack.append(("while", curr_i, stmt["condition"]))
                    self.pc += 1
                else:
                    # Skip to endwhile
                    i = curr_i + 1
                    while i < len(self.body) and self.body[i]["type"] != "endwhile":
                        i += 1
                    self.pc = i + 1

            elif t == "endwhile":
                if self.stack and self.stack[-1][0] == "while":
                    _, i_start, _ = self.stack[-1]
                    self.stack.pop()
                    self.pc = i_start  # Jump back to WHILE condition test
                else:
                    self.pc += 1

            # === BREAK / CONTINUE ===
            elif t == "break":
                # Find matching end for active loop
                i = curr_i + 1
                while i < len(self.body) and self.body[i]["type"] not in ("endwhile", "endfor", "endforeach"):
                    i += 1
                if self.stack:
                    self.stack.pop()
                self.pc = i + 1

            elif t == "continue":
                if self.stack:
                    loop_kind = self.stack[-1][0]
                    if loop_kind == "for":
                        i = curr_i + 1
                        while i < len(self.body) and self.body[i]["type"] != "endfor":
                            i += 1
                        self.pc = i  # Jump directly to endfor which increments
                    elif loop_kind == "foreach":
                        i = curr_i + 1
                        while i < len(self.body) and self.body[i]["type"] != "endforeach":
                            i += 1
                        self.pc = i
                    elif loop_kind == "while":
                        i = curr_i + 1
                        while i < len(self.body) and self.body[i]["type"] != "endwhile":
                            i += 1
                        self.pc = i
                else:
                    self.pc += 1

            # === DATA STRUCTURES ===
            elif t == "list_create":
                self.env[stmt["name"]] = eval(stmt["value"], {}, self.env)
                self.pc += 1

            elif t == "dict_create":
                self.env[stmt["name"]] = eval(stmt["value"], {}, self.env)
                self.pc += 1

            elif t == "list_append":
                self.env[stmt["list_name"]].append(eval(stmt["value"], {}, self.env))
                self.pc += 1

            elif t == "list_remove":
                self.env[stmt["list_name"]].remove(eval(stmt["value"], {}, self.env))
                self.pc += 1

            elif t == "get_value":
                self.env[stmt["target"]] = eval(stmt["source"], {}, self.env)
                self.pc += 1

            # === UTILITIES ===
            elif t == "sort":
                self.env[stmt["target"]] = sorted(self.env[stmt["source"]])
                self.pc += 1

            elif t == "filter":
                source = self.env[stmt["source"]]
                cond = stmt["condition"]
                self.env[stmt["target"]] = [x for x in source if eval(cond.replace("x", str(x)), {}, self.env)]
                self.pc += 1

            elif t == "map":
                source = self.env[stmt["source"]]
                expr = stmt["expression"]
                self.env[stmt["target"]] = [eval(expr.replace("x", str(x)), {}, self.env) for x in source]
                self.pc += 1

            elif t == "reduce":
                from functools import reduce
                source = self.env[stmt["source"]]
                expr = stmt["expression"]
                self.env[stmt["target"]] = reduce(lambda acc, x: eval(expr, {"acc": acc, "x": x}, {}), source)
                self.pc += 1

            # === ERROR HANDLING ===
            elif t == "try":
                self.try_stack.append(curr_i)
                self.pc += 1

            elif t == "catch":
                # Normal execution reached catch, skip to endtry
                i = curr_i + 1
                while i < len(self.body) and self.body[i]["type"] != "endtry":
                    i += 1
                self.pc = i + 1

            elif t == "endtry":
                if self.try_stack:
                    self.try_stack.pop()
                self.pc += 1

            # === FUNCTIONS / CALL ===
            elif t == "call":
                func = self.env.get(stmt["func_name"])
                if callable(func):
                    args = [eval(a, {}, self.env) for a in stmt.get("args", [])]
                    res = func(*args)
                    if stmt.get("result"):
                        self.env[stmt["result"]] = res
                self.pc += 1

            else:
                self.pc += 1

        except Exception as ex:
            if self.try_stack:
                # Jump to CATCH block
                i = curr_i + 1
                while i < len(self.body) and self.body[i]["type"] != "catch":
                    i += 1
                if i < len(self.body):
                    err_var = self.body[i].get("error_var", "error")
                    self.env[err_var] = str(ex)
                    self.pc = i + 1
            else:
                self.error = str(ex)
                self.is_finished = True

        # Calculate changed variables
        changed_vars = {}
        for k, v in self.env.items():
            if k not in env_before or env_before[k] != v:
                changed_vars[k] = v

        if self.pc >= len(self.body):
            self.is_finished = True

        state = StepperState(
            step_index=curr_i + 1,
            total_steps=self.total_steps,
            statement=stmt,
            statement_text=stmt_text,
            env=copy.copy(self.env),
            changed_vars=changed_vars,
            condition_info=condition_info,
            loop_info=loop_info,
            output_emitted=output_emitted,
            return_value=self.return_value,
            is_finished=self.is_finished,
            error=self.error
        )
        self.history.append(state)
        return state

    def run_all(self) -> List[StepperState]:
        """Runs all remaining steps to completion."""
        results = []
        max_steps = 10000  # Safeguard against infinite loops
        count = 0
        while not self.is_done() and count < max_steps:
            results.append(self.step())
            count += 1
        return results
