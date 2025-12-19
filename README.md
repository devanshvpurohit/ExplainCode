# ExplainCode 2.0 🧠💡

**ExplainCode 2.0** is a natural language programming language designed to bridge the gap between human logic and executable code. It allows you to build AI pipelines, manipulate data structures, and implement complex algorithms using a simple, readable syntax that "speaks your language."

---

## 🌟 Key Features (v2.0.0)

- 🤖 **AI Pipeline Support**: Native `LOAD_MODEL` and `PREDICT` steps using HuggingFace Transformers.
- 🗃️ **Complex Data Structures**: First-class support for `LIST` and `DICT` with `APPEND`, `REMOVE`, and `GET`.
- 📊 **Functional Utilities**: Built-in `SORT`, `FILTER`, `MAP`, and `REDUCE` operations.
- ⚠️ **Robust Error Handling**: Python-style `TRY`/`CATCH` blocks for graceful failure management.
- 🧠 **In-Memory Execution**: Direct execution of logic without residual intermediate files.
- 🖥️ **Dual Interface**: Use the clean CLI for scripting or the interactive PyQt5 IDE for visual development.

---

## 📦 Installation

To make ExplainCode available globally on your machine:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/devanshvpurohit/ExplainCode.git
   cd ExplainCode
   ```

2. **Install the package**:
   ```bash
   pip install .
   ```

---

## 🚀 Usage

### 🛠️ Command Line Interface
Run your ExplainCode files (`.epd`, `.eai`) directly from the terminal:

```bash
# Run a script immediately
explaincode examples/data_structures.epd

# Run with verbose output (see generated Python)
explaincode examples/data_structures.epd --verbose

# Run and save the underlying Python source
explaincode examples/data_structures.epd --save
```

### 🎨 Interactive IDE
Launch the visual editor and runner:
```bash
explaincode-gui
```

---

## 📜 Language Examples

### AI Sentiment Analysis
```plaintext
MODEL AnalyzeSentiment
INPUT: text
STEP 1: PRINT "Analyzing..."
STEP 2: LOAD_MODEL "sentiment-analysis" → model
STEP 3: PREDICT text → result
STEP 4: PRINT result
STEP 5: RETURN result
END MODEL
```

### Data Manipulation
```plaintext
ALGORITHM FilterHighNumbers
INPUT: numbers
STEP 1: SORT numbers → sorted_list
STEP 2: FILTER sorted_list WHERE x > 50 → high_nums
STEP 3: PRINT "High numbers found:"
STEP 4: PRINT high_nums
STEP 5: RETURN high_nums
END ALGORITHM
```

---

## 📁 Project Structure

```
ExplainCode/
├── explaincode/                # Core Package Source
│   ├── compiler.py             # Compiler & CLI logic
│   ├── interpreter.py          # GUI & AST Interpreter
│   └── lang/                   # Language Definitions
├── examples/                   # Built-in demo scripts
├── pyproject.toml              # Package configuration
└── README.md                   # Documentation
```

---

## 🤝 Contributing & Support

We welcome contributions! Fork the repo, add your features, and submit a PR.

- **Found a bug?** Open an [Issue](https://github.com/devanshvpurohit/ExplainCode/issues).
- **Have a feature idea?** Start a discussion.

---

## 📄 License

This project is licensed under the MIT License.

---
*Empowering ideas through code. One step at a time.* ✨

