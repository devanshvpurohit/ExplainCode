# explaincode_lang/

from pygls.server import LanguageServer
from pygls.lsp.types import Diagnostic, DiagnosticSeverity, Position, Range, DidOpenTextDocumentParams
from .parser import is_valid_explaincode, validate_lines

class ExplainCodeServer(LanguageServer):
    def __init__(self):
        super().__init__()

explain_server = ExplainCodeServer()

@explain_server.feature("textDocument/didOpen")
def did_open(ls: ExplainCodeServer, params: DidOpenTextDocumentParams):
    text = params.text_document.text
    lines = text.splitlines()
    diagnostics = []

    if not is_valid_explaincode(lines):
        diagnostics.append(Diagnostic(
            range=Range(start=Position(line=0, character=0), end=Position(line=0, character=100)),
            message="File must start with 'ALGORITHM' and end with 'END ALGORITHM'",
            severity=DiagnosticSeverity.Error
        ))

    issues = validate_lines(lines)
    for line_num, msg in issues:
        diagnostics.append(Diagnostic(
            range=Range(
                start=Position(line=line_num, character=0),
                end=Position(line=line_num, character=len(lines[line_num]))
            ),
            message=msg,
            severity=DiagnosticSeverity.Warning
        ))

    ls.publish_diagnostics(params.text_document.uri, diagnostics)
