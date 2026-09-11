"""
explaincode.learning_gui

PyQt5 GUI components for ExplainCode Learning Mode:
- ProgramStateWidget: Displays active variables, step tracer, and condition results.
- ConceptWidget: Displays AST concept breakdowns and pedagogical tips.
- ChallengeWidget: Interactive challenge runner with progressive hints and progression unlock.
- TransitionWidget: 5-level Python transition scaffolding (fill-in-the-blank & pure Python).
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QGroupBox, QSplitter, QTabWidget, QLineEdit,
    QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from .concepts import ConceptExplainer
from .challenges import CHALLENGES, ChallengeValidator, get_challenge_by_id
from .progression import ProgressionTracker
from .transition import TRANSITION_EXERCISES, TransitionManager
from .analytics import ResearchAnalytics


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

            # Highlight changed variables
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


class ConceptWidget(QWidget):
    """Displays AST concept explanations."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        title = QLabel("🧠 CONCEPT EXPLANATION")
        title.setStyleSheet("font-weight: bold; font-size: 13px; color: #202124;")
        layout.addWidget(title)

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setStyleSheet("font-family: sans-serif; font-size: 12px; line-height: 1.4;")
        self.text_area.setPlaceholderText("Click '💡 Explain' to inspect the programming concepts used in your algorithm.")
        layout.addWidget(self.text_area)

    def set_explanation(self, text: str):
        self.text_area.setText(text)


class ChallengeWidget(QWidget):
    """Panel for selecting, attempting, and testing challenges."""

    def __init__(self, progression: ProgressionTracker, analytics: ResearchAnalytics, parent=None):
        super().__init__(parent)
        self.progression = progression
        self.analytics = analytics
        self.current_hint_idx = 0
        self.on_load_code_fn = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Challenge selection & Progression
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("🎯 Challenge:"))
        self.combo = QComboBox()
        self.refresh_challenge_list()
        self.combo.currentIndexChanged.connect(self.on_challenge_selected)
        top_layout.addWidget(self.combo)

        load_btn = QPushButton("📥 Load Starter")
        load_btn.clicked.connect(self.load_starter_code)
        top_layout.addWidget(load_btn)
        layout.addLayout(top_layout)

        # Progression status label
        self.progression_label = QLabel("Progression: Loading...")
        self.progression_label.setStyleSheet("font-size: 11px; color: #1a73e8; font-weight: bold;")
        layout.addWidget(self.progression_label)

        # Problem statement
        self.problem_box = QTextEdit()
        self.problem_box.setReadOnly(True)
        self.problem_box.setMaximumHeight(90)
        self.problem_box.setStyleSheet("background-color: #f8f9fa; font-size: 12px;")
        layout.addWidget(self.problem_box)

        # Action buttons
        btn_layout = QHBoxLayout()
        self.hint_btn = QPushButton("💡 Hint (0/3)")
        self.hint_btn.clicked.connect(self.show_next_hint)
        btn_layout.addWidget(self.hint_btn)

        self.test_btn = QPushButton("🧪 Test Challenge")
        self.test_btn.setStyleSheet("font-weight: bold; background-color: #e8f0fe;")
        btn_layout.addWidget(self.test_btn)
        layout.addLayout(btn_layout)

        # Hints display
        self.hint_box = QTextEdit()
        self.hint_box.setReadOnly(True)
        self.hint_box.setMaximumHeight(80)
        self.hint_box.setPlaceholderText("Click '💡 Hint' for progressive hints.")
        self.hint_box.setStyleSheet("background-color: #fff9db; font-size: 12px;")
        layout.addWidget(self.hint_box)

        # Test results display
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        self.result_box.setStyleSheet("font-family: monospace; font-size: 12px;")
        layout.addWidget(self.result_box)

        self.update_view()

    def refresh_challenge_list(self):
        self.combo.clear()
        for ch in CHALLENGES:
            unlocked = self.progression.is_concept_unlocked(ch.concept)
            done = self.progression.is_challenge_completed(ch.id)
            status_icon = "✅" if done else ("🔓" if unlocked else "🔒")
            self.combo.addItem(f"{status_icon} [{ch.difficulty}] {ch.title} ({ch.concept})", ch.id)

    def on_challenge_selected(self):
        self.current_hint_idx = 0
        self.hint_box.clear()
        self.result_box.clear()
        self.update_view()

    def get_current_challenge(self):
        cid = self.combo.currentData()
        return get_challenge_by_id(cid)

    def update_view(self):
        ch = self.get_current_challenge()
        if not ch:
            return
        status = "Completed ✅" if self.progression.is_challenge_completed(ch.id) else "In Progress"
        self.problem_box.setText(
            f"Concept: {ch.concept} | Difficulty: {ch.difficulty} | Status: {status}\n\n"
            f"Problem: {ch.problem_statement}"
        )
        self.hint_btn.setText(f"💡 Hint ({self.current_hint_idx}/{len(ch.hints)})")

        overview = self.progression.get_status_overview()
        prog_text = "Progression: " + " ➔ ".join(
            f"[{c['concept']}: {'✓' if c['is_completed'] else ('🔓' if c['is_unlocked'] else '🔒')}]"
            for c in overview
        )
        self.progression_label.setText(prog_text)

    def load_starter_code(self):
        ch = self.get_current_challenge()
        if ch and self.on_load_code_fn:
            self.on_load_code_fn(ch.starter_code)

    def show_next_hint(self):
        ch = self.get_current_challenge()
        if not ch:
            return
        if self.current_hint_idx < len(ch.hints):
            hint_text = ch.hints[self.current_hint_idx]
            self.current_hint_idx += 1
            existing = self.hint_box.toPlainText()
            new_content = (existing + "\n\n" if existing else "") + hint_text
            self.hint_box.setText(new_content)
            self.hint_btn.setText(f"💡 Hint ({self.current_hint_idx}/{len(ch.hints)})")
            self.progression.record_hint_used(ch.id, self.current_hint_idx)
            self.analytics.record_hint(ch.id)
        else:
            QMessageBox.information(self, "Hints", "All available hints have been shown!")

    def run_tests(self, code_text: str):
        ch = self.get_current_challenge()
        if not ch:
            return

        self.analytics.start_challenge_attempt(ch.id, ch.concept, ch.difficulty)
        result = ChallengeValidator.validate_code(ch, code_text)

        lines = [f"🧪 Testing Challenge: {ch.title}\n"]
        if result.get("error"):
            lines.append(f"❌ {result['error']}")
            self.analytics.record_error(ch.id, "syntax")
            self.analytics.end_challenge_attempt(ch.id, False)
        else:
            passed_count = sum(1 for tc in result["test_results"] if tc["passed"])
            total_count = len(result["test_results"])

            for tc in result["test_results"]:
                icon = "✅" if tc["passed"] else "❌"
                inp_str = ", ".join(f"{k}={v}" for k, v in tc["inputs"].items()) or "none"
                lines.append(f"{icon} Test #{tc['test_case']} (Inputs: {inp_str})")
                lines.append(f"   Status: {tc['message']}")

            if result["passed"]:
                lines.append(f"\n🎉 SUCCESS! All {total_count} test cases passed!")
                self.progression.complete_challenge(ch.id, ch.concept)
                self.analytics.end_challenge_attempt(ch.id, True)
                self.refresh_challenge_list()
            else:
                lines.append(f"\n⚠️ {passed_count}/{total_count} test cases passed. Review hints and try again!")
                self.analytics.record_error(ch.id, "runtime")
                self.analytics.end_challenge_attempt(ch.id, False)

        self.result_box.setText("\n".join(lines))
        self.update_view()


class TransitionWidget(QWidget):
    """Interactive 5-Level Python Transition Widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.on_load_code_fn = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Header selector
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("🎓 Transition Exercise:"))
        self.combo = QComboBox()
        for ex in TRANSITION_EXERCISES:
            self.combo.addItem(f"{ex.title} ({ex.concept})", ex.id)
        self.combo.currentIndexChanged.connect(self.on_exercise_change)
        top_layout.addWidget(self.combo)
        layout.addLayout(top_layout)

        # Tab widget for Levels 1 through 5
        self.tabs = QTabWidget()

        # Level 1: Natural Language
        self.lvl1_widget = QTextEdit()
        self.lvl1_widget.setReadOnly(True)
        self.tabs.addTab(self.lvl1_widget, "Level 1: Natural Logic")

        # Level 2: ExplainCode
        l2_widget = QWidget()
        l2_layout = QVBoxLayout(l2_widget)
        self.lvl2_text = QTextEdit()
        self.lvl2_text.setReadOnly(True)
        self.lvl2_btn = QPushButton("📥 Copy to Main Editor")
        self.lvl2_btn.clicked.connect(self.load_l2_code)
        l2_layout.addWidget(self.lvl2_text)
        l2_layout.addWidget(self.lvl2_btn)
        self.tabs.addTab(l2_widget, "Level 2: ExplainCode")

        # Level 3: Dual View
        l3_widget = QWidget()
        l3_layout = QHBoxLayout(l3_widget)
        self.lvl3_epd = QTextEdit()
        self.lvl3_epd.setReadOnly(True)
        self.lvl3_py = QTextEdit()
        self.lvl3_py.setReadOnly(True)
        l3_layout.addWidget(self.lvl3_epd)
        l3_layout.addWidget(self.lvl3_py)
        self.tabs.addTab(l3_widget, "Level 3: Side-by-Side")

        # Level 4: Complete Blanks
        l4_widget = QWidget()
        l4_layout = QVBoxLayout(l4_widget)
        self.lvl4_scaffold = QTextEdit()
        self.lvl4_scaffold.setReadOnly(True)
        self.lvl4_scaffold.setMaximumHeight(120)
        l4_layout.addWidget(self.lvl4_scaffold)

        l4_layout.addWidget(QLabel("Fill in blanks (comma-separated if multiple):"))
        self.lvl4_input = QLineEdit()
        self.lvl4_input.setPlaceholderText("e.g. 10 or 5, x")
        l4_layout.addWidget(self.lvl4_input)

        self.lvl4_verify_btn = QPushButton("✅ Check Blanks")
        self.lvl4_verify_btn.clicked.connect(self.check_level4)
        l4_layout.addWidget(self.lvl4_verify_btn)

        self.lvl4_feedback = QLabel("")
        self.lvl4_feedback.setWordWrap(True)
        l4_layout.addWidget(self.lvl4_feedback)
        self.tabs.addTab(l4_widget, "Level 4: Fill Python Blanks")

        # Level 5: Write Independent Python
        l5_widget = QWidget()
        l5_layout = QVBoxLayout(l5_widget)
        self.lvl5_prompt = QLabel("")
        self.lvl5_prompt.setWordWrap(True)
        self.lvl5_prompt.setStyleSheet("font-weight: bold; color: #1a73e8;")
        l5_layout.addWidget(self.lvl5_prompt)

        self.lvl5_editor = QTextEdit()
        self.lvl5_editor.setStyleSheet("font-family: monospace; font-size: 12px;")
        l5_layout.addWidget(self.lvl5_editor)

        self.lvl5_test_btn = QPushButton("🚀 Run Python Tests")
        self.lvl5_test_btn.clicked.connect(self.test_level5)
        l5_layout.addWidget(self.lvl5_test_btn)

        self.lvl5_feedback = QTextEdit()
        self.lvl5_feedback.setReadOnly(True)
        self.lvl5_feedback.setMaximumHeight(90)
        l5_layout.addWidget(self.lvl5_feedback)
        self.tabs.addTab(l5_widget, "Level 5: Pure Python")

        layout.addWidget(self.tabs)
        self.on_exercise_change()

    def get_current_exercise(self):
        eid = self.combo.currentData()
        return TransitionManager.get_exercise_by_id(eid)

    def on_exercise_change(self):
        ex = self.get_current_exercise()
        if not ex:
            return

        self.lvl1_widget.setText(f"=== {ex.title} ({ex.concept}) ===\n\n{ex.level1_description}")
        self.lvl2_text.setText(ex.level2_explaincode)
        self.lvl3_epd.setText(f"# ExplainCode\n\n{ex.level2_explaincode}")
        self.lvl3_py.setText(f"# Equivalent Python\n\n{ex.level3_python}")
        self.lvl4_scaffold.setText(ex.level4_scaffold)
        self.lvl4_input.clear()
        self.lvl4_feedback.setText("")
        self.lvl5_prompt.setText(ex.level5_prompt)
        self.lvl5_editor.setText(f"# Write pure Python solution below:\n")
        self.lvl5_feedback.clear()

    def load_l2_code(self):
        ex = self.get_current_exercise()
        if ex and self.on_load_code_fn:
            self.on_load_code_fn(ex.level2_explaincode)

    def check_level4(self):
        ex = self.get_current_exercise()
        if not ex:
            return
        text = self.lvl4_input.text()
        answers = [a.strip() for a in text.split(",") if a.strip()]
        ok, msg = TransitionManager.validate_level4(ex, answers)
        color = "green" if ok else "red"
        self.lvl4_feedback.setText(f"<font color='{color}'>{msg}</font>")

    def test_level5(self):
        ex = self.get_current_exercise()
        if not ex:
            return
        code = self.lvl5_editor.toPlainText()
        ok, msg = TransitionManager.validate_level5(code, ex.level5_test_cases)
        icon = "✅" if ok else "❌"
        self.lvl5_feedback.setText(f"{icon} {msg}")
