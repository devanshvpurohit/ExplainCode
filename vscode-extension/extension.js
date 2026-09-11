/**
 * ExplainCode VS Code Extension
 * Provides syntax highlighting, commands for Show Python, Explain Concepts,
 * Step execution, Learning Mode IDE launcher, and live diagnostics.
 */

const vscode = require('vscode');
const cp = require('child_process');
const path = require('path');

let diagnosticCollection;

function activate(context) {
    diagnosticCollection = vscode.languages.createDiagnosticCollection('explaincode');
    context.subscriptions.push(diagnosticCollection);

    // 1. Show Equivalent Python command
    const showPythonCmd = vscode.commands.registerCommand('explaincode.showPython', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active ExplainCode file open.');
            return;
        }

        const code = editor.document.getText();
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "ExplainCode: Generating Equivalent Python..."
        }, () => {
            return new Promise((resolve) => {
                const pyProcess = cp.spawn('python3', [
                    '-c',
                    `import sys, json
from explaincode.compiler import ExplainCodeParser, ExplainCodeCompiler
try:
    code = sys.stdin.read()
    ast = ExplainCodeParser().parse(code.splitlines())
    print(ExplainCodeCompiler(ast).compile())
except Exception as e:
    sys.stderr.write(str(e))
    sys.exit(1)`
                ]);

                let stdout = '';
                let stderr = '';

                pyProcess.stdout.on('data', (d) => stdout += d);
                pyProcess.stderr.on('data', (d) => stderr += d);

                pyProcess.on('close', async (exitCode) => {
                    resolve();
                    if (exitCode === 0) {
                        const doc = await vscode.workspace.openTextDocument({
                            content: stdout,
                            language: 'python'
                        });
                        await vscode.window.showTextDocument(doc, {
                            viewColumn: vscode.ViewColumn.Beside,
                            preview: true
                        });
                    } else {
                        vscode.window.showErrorMessage(`ExplainCode Compilation Error: ${stderr}`);
                    }
                });

                pyProcess.stdin.write(code);
                pyProcess.stdin.end();
            });
        });
    });

    // 2. Explain Concepts command
    const explainConceptsCmd = vscode.commands.registerCommand('explaincode.explainConcepts', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active ExplainCode file open.');
            return;
        }

        const code = editor.document.getText();
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "ExplainCode: Analyzing Programming Concepts..."
        }, () => {
            return new Promise((resolve) => {
                const pyProcess = cp.spawn('python3', [
                    '-c',
                    `import sys
from explaincode.compiler import ExplainCodeParser
from explaincode.concepts import explain_code
try:
    code = sys.stdin.read()
    ast = ExplainCodeParser().parse(code.splitlines())
    print(explain_code(ast))
except Exception as e:
    sys.stderr.write(str(e))
    sys.exit(1)`
                ]);

                let stdout = '';
                let stderr = '';

                pyProcess.stdout.on('data', (d) => stdout += d);
                pyProcess.stderr.on('data', (d) => stderr += d);

                pyProcess.on('close', (exitCode) => {
                    resolve();
                    if (exitCode === 0) {
                        const panel = vscode.window.createWebviewPanel(
                            'explaincodeConcepts',
                            '🧠 ExplainCode Concepts',
                            vscode.ViewColumn.Beside,
                            { enableScripts: true }
                        );
                        panel.webview.html = getConceptsWebviewHtml(stdout);
                    } else {
                        vscode.window.showErrorMessage(`ExplainCode Error: ${stderr}`);
                    }
                });

                pyProcess.stdin.write(code);
                pyProcess.stdin.end();
            });
        });
    });

    // 3. Open Learning Mode GUI
    const openLearningModeCmd = vscode.commands.registerCommand('explaincode.openLearningMode', () => {
        const editor = vscode.window.activeTextEditor;
        const filePath = editor ? editor.document.fileName : '';

        vscode.window.showInformationMessage('Launching ExplainCode Learning Mode IDE...');
        const child = cp.spawn('python3', ['-m', 'explaincode.interpreter'], {
            detached: true,
            stdio: 'ignore'
        });
        child.unref();
    });

    // 4. Run file in Terminal
    const runFileCmd = vscode.commands.registerCommand('explaincode.runFile', () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active ExplainCode file open.');
            return;
        }

        const filePath = editor.document.fileName;
        const terminal = vscode.window.activeTerminal || vscode.window.createTerminal('ExplainCode');
        terminal.show();
        terminal.sendText(`python3 -m explaincode.compiler "${filePath}"`);
    });

    // 5. Open Challenges Webview
    const openChallengesCmd = vscode.commands.registerCommand('explaincode.openChallenges', () => {
        const panel = vscode.window.createWebviewPanel(
            'explaincodeChallenges',
            '🎯 ExplainCode Challenges',
            vscode.ViewColumn.Beside,
            { enableScripts: true }
        );
        panel.webview.html = getChallengesWebviewHtml();
    });

    // 6. Real-time document diagnostics
    vscode.workspace.onDidSaveTextDocument(validateDocument);
    vscode.workspace.onDidOpenTextDocument(validateDocument);
    if (vscode.window.activeTextEditor) {
        validateDocument(vscode.window.activeTextEditor.document);
    }

    context.subscriptions.push(
        showPythonCmd,
        explainConceptsCmd,
        openLearningModeCmd,
        runFileCmd,
        openChallengesCmd
    );
}

function validateDocument(document) {
    if (document.languageId !== 'explaincode') return;

    const text = document.getText();
    const pyProcess = cp.spawn('python3', [
        '-c',
        `import sys, json
from explaincode.errors import ErrorTutor
code = sys.stdin.read().splitlines()
diag = ErrorTutor.diagnose_syntax(code)
if diag:
    print(json.dumps({
        "problem": diag.problem,
        "concept": diag.concept,
        "suggestion": diag.suggestion,
        "line": diag.line_number or 1,
        "error": diag.technical_error
    }))
else:
    print("{}")`
    ]);

    let stdout = '';
    pyProcess.stdout.on('data', (d) => stdout += d);

    pyProcess.on('close', (exitCode) => {
        if (exitCode === 0 && stdout.trim()) {
            try {
                const info = JSON.parse(stdout);
                if (info.problem) {
                    const lineIdx = Math.max(0, (info.line || 1) - 1);
                    const line = document.lineAt(Math.min(lineIdx, document.lineCount - 1));
                    const diagnostic = new vscode.Diagnostic(
                        line.range,
                        `${info.problem} (${info.concept})\nSuggestion: ${info.suggestion}`,
                        vscode.DiagnosticSeverity.Error
                    );
                    diagnostic.source = 'ExplainCode';
                    diagnosticCollection.set(document.uri, [diagnostic]);
                    return;
                }
            } catch (e) {}
        }
        diagnosticCollection.set(document.uri, []);
    });

    pyProcess.stdin.write(text);
    pyProcess.stdin.end();
}

function getConceptsWebviewHtml(conceptText) {
    const formatted = conceptText
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\n/g, '<br/>');

    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ExplainCode Concepts</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 20px; line-height: 1.6; }
        h1 { color: #1a73e8; border-bottom: 2px solid #e8f0fe; padding-bottom: 8px; }
        .card { background: var(--vscode-editor-background); border: 1px solid var(--vscode-widget-border); padding: 15px; border-radius: 6px; font-family: monospace; white-space: pre-wrap; }
    </style>
</head>
<body>
    <h1>🧠 Programming Concepts Explained</h1>
    <div class="card">${conceptText}</div>
</body>
</html>`;
}

function getChallengesWebviewHtml() {
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ExplainCode Challenges</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 20px; }
        h1 { color: #1a73e8; }
        .challenge { border: 1px solid #ccc; padding: 12px; margin-bottom: 12px; border-radius: 6px; }
        .title { font-weight: bold; font-size: 14px; }
        .badge { display: inline-block; background: #e8f0fe; color: #1a73e8; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-left: 8px; }
    </style>
</head>
<body>
    <h1>🎯 Practice Challenges</h1>
    <p>Practice programming concepts by solving ExplainCode challenges.</p>

    <div class="challenge">
        <span class="title">1. Student Marks Storage</span><span class="badge">Beginner · Variables</span>
        <p>Store a student's marks (85) in a variable named 'marks' and display them.</p>
    </div>

    <div class="challenge">
        <span class="title">2. Welcome Greeting</span><span class="badge">Beginner · Input / Output</span>
        <p>Accept a user's name and display "Hello, " followed by the name.</p>
    </div>

    <div class="challenge">
        <span class="title">3. Positive or Negative</span><span class="badge">Beginner · Conditions</span>
        <p>Determine whether an input number is positive or negative.</p>
    </div>

    <div class="challenge">
        <span class="title">4. Counting 1 to 10</span><span class="badge">Beginner · Loops</span>
        <p>Display numbers from 1 to 10 using a FOR loop.</p>
    </div>

    <div class="challenge">
        <span class="title">5. Find Largest Number</span><span class="badge">Intermediate · Lists</span>
        <p>Find and return the largest number in a list.</p>
    </div>

    <div class="challenge">
        <span class="title">6. Calculate Square</span><span class="badge">Intermediate · Functions</span>
        <p>Calculate and return the square of a given number.</p>
    </div>
</body>
</html>`;
}

function deactivate() {
    if (diagnosticCollection) {
        diagnosticCollection.clear();
        diagnosticCollection.dispose();
    }
}

module.exports = {
    activate,
    deactivate
};
