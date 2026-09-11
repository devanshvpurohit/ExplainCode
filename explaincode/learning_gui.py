"""
explaincode.learning_gui

PyQt5 GUI components for ExplainCode:
- ProgramStateWidget: Displays active variables, step tracer, and condition results.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtGui import QColor


class ProgramStateWidget(QWidget):
    """Displays live execution state: active variables, condition results, and current step."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Current Step Card
        step_group = QGroupBox("📌 CURRENT STEP")
        step_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        step_layout = QVBoxLayout(step_group)

        self.step_label = QLabel("Statement: Ready to run or step.")
        self.step_label.setWordWrap(True)
        self.step_label.setStyleSheet("font-family: monospace; font-size: 13px; color: #1a73e8;")

        self.condition_label = QLabel("Condition: -")
        self.condition_label.setWordWrap(True)
        self.condition_label.setStyleSheet("font-size: 12px; color: #555;")

        self.loop_label = QLabel("Loop State: -")
        self.loop_label.setWordWrap(True)
        self.loop_label.setStyleSheet("font-size: 12px; color: #555;")

        step_layout.addWidget(self.step_label)
        step_layout.addWidget(self.condition_label)
        step_layout.addWidget(self.loop_label)
        layout.addWidget(step_group)

        # Variables Table
        vars_group = QGroupBox("📊 PROGRAM STATE (Variables)")
        vars_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        vars_layout = QVBoxLayout(vars_group)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Variable", "Value"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("QTableWidget { font-family: monospace; font-size: 12px; }")
        vars_layout.addWidget(self.table)

        layout.addWidget(vars_group)

    def update_state(self, state_dict: dict):
        # Update statement
        stmt_text = state_dict.get("statement_text", "")
        idx = state_dict.get("step_index", 0)
        tot = state_dict.get("total_steps", 0)
        prefix = f"Step {idx}/{tot}: " if tot else ""
        self.step_label.setText(f"{prefix}{stmt_text}")

        # Update condition
        cond_info = state_dict.get("condition_info")
        if cond_info:
            cond_str = cond_info.get("condition", "")
            res = "TRUE" if cond_info.get("result") else "FALSE"
            branch = cond_info.get("branch_taken", "")
            self.condition_label.setText(f"Condition: {cond_str} ➜ {res} ({branch})")
        else:
            self.condition_label.setText("Condition: -")

        # Update loop info
        loop_info = state_dict.get("loop_info")
        if loop_info:
            l_var = loop_info.get("variable", "")
            l_val = loop_info.get("current_value", "")
            if loop_info.get("completed"):
                self.loop_label.setText(f"Loop on '{l_var}': Finished")
            else:
                self.loop_label.setText(f"Loop iteration: {l_var} = {l_val}")
        else:
            self.loop_label.setText("Loop State: -")

        # Update variables table
        variables = state_dict.get("variables", {})
        changed = state_dict.get("changed_vars", {})

        self.table.setRowCount(len(variables))
        for row, (var_name, var_val) in enumerate(variables.items()):
            item_name = QTableWidgetItem(str(var_name))
            item_val = QTableWidgetItem(str(var_val))

            if var_name in changed:
                item_name.setBackground(QColor("#d4edda"))
                item_val.setBackground(QColor("#d4edda"))

            self.table.setItem(row, 0, item_name)
            self.table.setItem(row, 1, item_val)

    def clear(self):
        self.step_label.setText("Statement: Ready")
        self.condition_label.setText("Condition: -")
        self.loop_label.setText("Loop State: -")
        self.table.setRowCount(0)
