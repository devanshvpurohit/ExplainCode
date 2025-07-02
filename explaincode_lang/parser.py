# explaincode_lang/parser.py

def is_valid_explaincode(lines):
    return lines[0].startswith("ALGORITHM") and lines[-1].strip() == "END ALGORITHM"

def validate_lines(lines):
    diagnostics = []
    for i, line in enumerate(lines):
        if "Set" in line and "←" not in line:
            diagnostics.append((i, "Missing assignment operator '←'"))
        if "IF" in line and "THEN" not in line:
            diagnostics.append((i, "Missing THEN in IF statement"))
    return diagnostics
