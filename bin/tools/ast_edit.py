import libcst as cst
import json
import os
import re

class MethodReplacementTransformer(cst.CSTTransformer):
    def __init__(self, method_name, new_code):
        self.method_name = method_name
        self.new_node = cst.parse_statement(new_code)
        self.found = False

    def leave_FunctionDef(self, original_node, updated_node):
        if original_node.name.value == self.method_name:
            self.found = True
            return self.new_node
        return updated_node

class ClassReplacementTransformer(cst.CSTTransformer):
    def __init__(self, class_name, new_code):
        self.class_name = class_name
        self.new_node = cst.parse_statement(new_code)
        self.found = False

    def leave_ClassDef(self, original_node, updated_node):
        if original_node.name.value == self.class_name:
            self.found = True
            return self.new_node
        return updated_node

class AddFunctionTransformer(cst.CSTTransformer):
    def __init__(self, func_code):
        self.func_node = cst.parse_statement(func_code)

    def leave_Module(self, original_node, updated_node):
        new_body = list(updated_node.body)
        new_body.append(self.func_node)
        return updated_node.with_changes(body=new_body)

def execute(payload):
    """
    Atlas Tool: Performs precise AST-based code modification using libcst.
    Payload: {
        "path": "relative/path/to/file.py",
        "action": "replace_method | add_function | replace_class",
        "target": "name_of_method_or_class",
        "code": "complete_code_of_new_node"
    }
    """
    try:
        if isinstance(payload, str):
            data = json.loads(payload)
        else:
            data = payload
            
        file_path = data.get("path")
        action = data.get("action")
        target = data.get("target")
        code_to_inject = data.get("code")
        
        # Ensure path is relative to AGENT_ROOT for safety
        if file_path.startswith('/'):
            file_path = file_path.lstrip('/')
            
        if not os.path.exists(file_path):
            return f"Error: File {file_path} not found."

        with open(file_path, "r") as f:
            source_code = f.read()

        module = cst.parse_module(source_code)
        
        if action == "add_function":
            transformer = AddFunctionTransformer(code_to_inject)
            modified_module = module.visit(transformer)
            msg = f"AST: Successfully appended function to {file_path}."
            
        elif action == "replace_method":
            transformer = MethodReplacementTransformer(target, code_to_inject)
            modified_module = module.visit(transformer)
            if not transformer.found:
                return f"Error: Method '{target}' not found in {file_path}."
            msg = f"AST: Successfully replaced method '{target}' in {file_path}."

        elif action == "replace_class":
            transformer = ClassReplacementTransformer(target, code_to_inject)
            modified_module = module.visit(transformer)
            if not transformer.found:
                return f"Error: Class '{target}' not found in {file_path}."
            msg = f"AST: Successfully replaced class '{target}' in {file_path}."
            
        else:
            return f"Error: Unknown AST action {action}"

        with open(file_path, "w") as f:
            f.write(modified_module.code)
        return msg

    except Exception as e:
        return f"AST Error: {str(e)}"
