
# ExplainCode 2.0 🧠💡
A Human-Centric Natural Language Programming Language for AI Workflows and Algorithmic Reasoning

---

## 🌟 Overview

**ExplainCode 2.0** is a domain-specific programming language that bridges the gap between natural logic and executable code. Designed for **AI prototyping**, **algorithmic education**, and **intuitive computing**, it allows users to write code using simple, human-readable steps.

> No more confusing syntax. Just logic that *speaks your language*.

---

## 🔧 Features

- 🔤 **Natural Language Syntax** – Use keywords like `STEP`, `Set`, `IF`, `MODEL`, and `DISPLAY`
- 🧠 **AI-Aware Constructs** – Seamless pipelines for sentiment analysis, visualization, ML models
- ⚡ **Dual Execution** – Compile to Python *or* interpret directly for instant feedback
- 🎓 **Education-Friendly** – Perfect for students learning algorithms and program flow
- 🖥️ **PyQt5 IDE** – A complete GUI for editing, running, and debugging `.ec2` and `.modelx` files

---

## 📦 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/explaincode.git
cd explaincode
````

### 2. Install Requirements

```bash
pip install -r requirements.txt
```

### 3. Run the IDE

```bash
python explaincode_gui.py
```

---

## 🚀 Hello, ExplainCode

Here’s an example of finding the maximum of two numbers:

```plaintext
DEFINE MaxOfTwo
INPUT: a, b
OUTPUT: result
STEP 1: IF a > b THEN
STEP 2:     Set result ← a
STEP 3: ELSE
STEP 4:     Set result ← b
STEP 5: END IF
STEP 6: DISPLAY result
STEP 7: RETURN result
END DEFINE
```

Or a sentiment analysis model using HuggingFace Transformers:

```plaintext
MODEL AnalyzeText
INPUT: text
OUTPUT: mood
STEP 1: USE transformers
STEP 2: Set pipe ← transformers.pipeline("sentiment-analysis")
STEP 3: Set mood ← pipe(text)
STEP 4: DISPLAY mood
STEP 5: RETURN mood
END MODEL
```

---

## 🧪 Use Cases

* 🤖 **AI Prototyping** — Build models with no boilerplate
* 📊 **Data Visualization** — Generate graphs in plain language
* 🧩 **Teaching & Learning** — Ideal for educators and CS students
* 📜 **Explainable Logic** — Clear, self-documenting code

---

## 📁 Project Structure

```
explaincode/
├── parser/
│   └── explain_parser.py
├── compiler/
│   └── codegen.py
├── interpreter/
│   └── runner.py
├── gui/
│   └── explaincode_gui.py
├── examples/
│   ├── sentiment_analysis.modelx
│   └── max_two.ec2
└── README.md
```

---

## 🧠 Future Plans

* 🧰 Visual debugger + flowchart mode
* 🤝 Real-time collaboration support
* 🐍 OOP-style blocks and class support
* 🧮 Built-in data structure tools

---

## 🤝 Contributing

We welcome contributions! Feel free to fork, improve, and submit pull requests.

```bash
git checkout -b feature/your-feature
git commit -m "Added your feature"
git push origin feature/your-feature
```

---

## 📄 License

This project is licensed under the MIT License.
See [LICENSE](LICENSE) for more information.

---

## 💬 Connect

For questions, feedback, or collaboration:

* 📧 Email: [you@example.com](mailto:you@example.com)
* 🌐 Website: [https://explaincode.ai](https://explaincode.ai)
* 🐦 Twitter: [@explaincode](https://twitter.com/explaincode)

---

Empowering ideas through code. One step at a time. ✨

```

---

Let me know if you'd like:
- The same content tailored for an academic repo
- Auto-generated badges (PyPI, GitHub Actions, etc.)
- Multi-language examples (e.g., integrating with JavaScript or C++)
```
