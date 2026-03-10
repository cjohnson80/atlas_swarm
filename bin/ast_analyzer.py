import ast
import os
import json

class AtlasASTAnalyzer:
    """
    Elite AST-based code analysis for architectural topology mapping.
    Transscends text-grep by understanding scope, imports, and class hierarchies.
    """
    def __init__(self, root_dir):
        self.root_dir = root_dir

    def map_file(self, file_path):
        if not file_path.endswith('.py'):
            return {"error": "Only Python files supported for AST mapping."}
        
        try:
            with open(file_path, "r") as f:
                tree = ast.parse(f.read())
        except Exception as e:
            return {"error": f"AST Parse Error: {str(e)}"}

        mapping = {
            "classes": [],
            "functions": [],
            "imports": [],
            "summary": ""
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                mapping["classes"].append({
                    "name": node.name,
                    "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                    "line": node.lineno
                })
            elif isinstance(node, ast.FunctionDef) and not isinstance(getattr(node, 'parent', None), ast.ClassDef):
                # Filter for top-level functions
                mapping["functions"].append({
                    "name": node.name,
                    "line": node.lineno
                })
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        mapping["imports"].append(alias.name)
                else:
                    mapping["imports"].append(f"{node.module}.{node.names[0].name}")

        mapping["summary"] = f"Mapped {len(mapping['classes'])} classes and {len(mapping['functions'])} functions."
        return mapping

    def get_topology(self, target_dir=None):
        """Builds a dependency graph and architectural map of the directory."""
        target_dir = target_dir or self.root_dir
        topology = {}
        
        for root, _, files in os.walk(target_dir):
            for file in files:
                if file.endswith('.py'):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.root_dir)
                    topology[rel_path] = self.map_file(full_path)
        
        return topology

if __name__ == "__main__":
    analyzer = AtlasASTAnalyzer(os.path.expanduser("~/atlas_agents"))
    print(json.dumps(analyzer.get_topology("bin"), indent=2))
