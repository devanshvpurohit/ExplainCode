# ExplainCode 2.0 VS Code Extension 🧠💡

The official Visual Studio Code extension for **ExplainCode 2.0** — the natural-language programming language designed to bridge the gap between algorithmic thinking and Python programming.

---

## 🌟 Features

- 🎨 **Syntax Highlighting**: Full TextMate grammar support for ExplainCode (`.epd`, `.eai`, `.explain`) scripts.
- 🐍 **Show Equivalent Python**: Live, one-click side-by-side Python generation powered by `ExplainCodeCompiler`.
- 💡 **Explain Concepts**: AST-driven pedagogical breakdown explaining the programming concepts (Variables, Conditionals, Loops, Lists, Dicts, Functions, Return, Error Handling) in your algorithm.
- 🎯 **Interactive Challenges**: Graded challenges with automated test cases and multi-tier progressive hints.
- 🔍 **Live Pedagogical Diagnostics**: Real-time error detection displaying beginner explanations alongside technical errors.
- 🚀 **Learning Mode IDE**: One-click launch of the full PyQt5 Learning Mode IDE with step-by-step variable tracing and 5-level Python transition.

---

## 📦 Requirements

- Python 3.8+ with `explaincode` package installed (`pip install -e .` from the repository root).
- PyQt5 (for the interactive GUI).

---

## 🛠️ Usage

1. Open any ExplainCode file (`.epd` or `.eai`).
2. Click the editor action buttons in the top right:
   - **`🐍 Show Python`**: Generates and displays equivalent Python beside your code.
   - **`💡 Explain Concepts`**: Shows what programming concepts your code utilizes.
   - **`▶ Open Learning Mode`**: Launches the visual interactive learning environment.
3. Or use the Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`):
   - `ExplainCode: Show Equivalent Python`
   - `ExplainCode: Explain Concepts`
   - `ExplainCode: Open Learning Mode GUI`
   - `ExplainCode: Run File in Terminal`
   - `ExplainCode: Open Learning Challenges`

---

## 📄 License

MIT License.
