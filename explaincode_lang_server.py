

try:
    from explaincode.lang.lsp_server import explain_server
except ImportError:
    from explaincode_lang.lsp_server import explain_server

if __name__ == "__main__":
    explain_server.start_io()
