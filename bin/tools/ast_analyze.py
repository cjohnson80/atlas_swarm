import libcst as cst
import json
import os

class CodeAnalyzer(cst.CSTVisitor):
    def __init__(self):
        self.metadata = {
            "classes": [],
            "functions": [],
            "imports": []
        }

    def visit_ClassDef(self, node: cst.ClassDef):
        methods = []
        for item in node.body.body:
            if isinstance(item, cst.FunctionDef):
                methods.append(item.name.value)
        self.metadata["classes"].append({
            "name": node.name.value,
            "methods": methods
        })

    def visit_FunctionDef(self, node: cst.FunctionDef):
        # Only top-level functions (not methods)
        self.metadata["functions"].append(node.name.value)

    def visit_Import(self, node: cst.Import):
        for name in node.names:
            self.metadata["imports"].append(name.name.value)

    def visit_ImportFrom(self, node: cst.ImportFrom):
        module = node.module.value if node.module else ""
        for name in node.names:
            self.metadata["imports"].append(f"{module}.{name.name.value}")

def execute(payload):
    """
    Atlas Tool: Performs deep AST-based code analysis.
    Payload: "path/to/file.py"
    """
    try:
        file_path = str(payload).strip()
        if file_path.startswith('/'):
            file_path = file_path.lstrip('/')
            
        if not os.path.exists(file_path):
            return f"Error: File {file_path} not found."

        with open(file_path, "r") as f:
            source_code = f.read()

        module = cst.parse_module(source_code)
        analyzer = CodeAnalyzer()
        module.visit(analyzer)
        
        return json.dumps(analyzer.metadata, indent=2)

    except Exception as e:
        return f"AST Analysis Error: {str(e)}"
