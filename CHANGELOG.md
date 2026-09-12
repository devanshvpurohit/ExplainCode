# ExplainCode Releases

## [3.0.0] - ExplainCode 3.0
### Changed
- Replaced the assignment operator `←` with `==` to make syntax more intuitive and standard.
- Updated all parser components, error tutors, and examples to use `==` for assignment.
- Removed unused learning modules (Concepts, Challenges, Progression, Analytics, Transition) from the native GUI to focus strictly on a unified, streamlined Python programming environment.
- Stripped `learning_gui.py` down to just the highly effective `ProgramStateWidget` (live execution state, variable tables, conditions).
- Updated VS Code Extension manifest to version 3.0.0.

### Added
- Several new comprehensive code examples:
  - `sum_of_list.epd`: Summing an array of numbers.
  - `sum_of_digits.epd`: Summing individual digits of a number.
  - `sum_two_numbers.epd`: Simple addition of two inputs.
  - `longest_unique_substring.epd`: Finding the longest substring without repeating characters using the sliding window algorithm.
  - `fizzbuzz.epd`, `fibonacci.epd`, `factorial.epd`, `palindrome_check.epd`.
- Added comprehensive unit test coverage:
  - **Parser coverage**: empty file handling, missing headers, import statements.
  - **Execution correctness**: step-by-step state verification using Fibonacci logic.
  - **Compilation correctness**: parsing and executing Python for the FizzBuzz logic.
  - **Error diagnostics**: unbalanced loops, missing headers, missing assignment operators.

---

## [2.0.0] - ExplainCode 2.0
### Added
- Created the core ExplainCode pedagogical programming language designed to bridge the gap between algorithmic pseudocode and executable Python.
- Real-time compiler (`compiler.py`) and step-by-step runtime tracer (`stepper.py`).
- Built a rich pedagogical GUI (`explaincode-gui`) displaying Program State dynamically via PyQt5.
- Added comprehensive Beginner Explanation + Technical Error diagnostics framework (`errors.py`) translating Python tracebacks and syntax errors into plain English.
- Official Visual Studio Code extension (packaged as `.vsix`) with real-time diagnostics, syntax highlighting, and execution commands.
