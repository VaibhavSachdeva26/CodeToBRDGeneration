import ast
import re


def clean_code(code):
    """
    Cleans Python code by removing comments, unnecessary whitespace, and docstrings.
    """

    # Remove comments using regular expressions
    code = re.sub(r'#.*', '', code)

    # Parse the code into AST
    tree = ast.parse(code)

    # Remove docstrings
    class CodeCleaner(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            if ast.get_docstring(node):
                node.body = [n for n in node.body if not isinstance(n, ast.Expr)]
            return self.generic_visit(node)

    cleaner = CodeCleaner()
    cleaned_tree = cleaner.visit(tree)

    # Convert the cleaned AST back to code
    cleaned_code = ast.unparse(cleaned_tree)

    # Strip unnecessary whitespace
    #cleaned_code = '\n'.join(line.strip() for line in cleaned_code.splitlines() if line.strip())

    return cleaned_code


def extract_code_components(code):
    """
    Extracts function definitions, function calls, and external dependencies (import statements) from Python code.
    """

    # Parse the code into AST
    tree = ast.parse(code)

    function_definitions = []
    function_calls = []
    external_dependencies = []

    # Walk through AST nodes to find different components
    for node in ast.walk(tree):

        # Function definitions
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            func_code = ast.get_source_segment(code, node)
            function_definitions.append((func_name, func_code))

        # Function calls
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            call_name = node.func.id
            call_code = ast.get_source_segment(code, node)
            function_calls.append((call_name, call_code))

        # External dependencies (import statements)
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            import_code = ast.get_source_segment(code, node)
            external_dependencies.append(import_code)

    return function_definitions, function_calls, external_dependencies


def process_python_code(file_path):
    """
    Process a Python code file: clean the code, and extract components (functions, calls, imports).
    """
    # Read the Python file

    with open(file_path, 'r') as f:
        code = f.read()
    #later change the python code text from extract text file

    # Clean the code
    cleaned_code = clean_code(code)

    # Extract code components
    function_definitions, function_calls, external_dependencies = extract_code_components(cleaned_code)

    return {
        "cleaned_code": cleaned_code,
        "function_definitions": function_definitions,
        "function_calls": function_calls,
        "external_dependencies": external_dependencies
    }


# Example usage
if __name__ == '__main__':
    file_path = r'C:\Users\Vaibhav\Desktop\POC\CodeToBRD\CodeToBRD_LLM\Preprocessing\extract_text.py'  # Replace with your Python file path
    result = process_python_code(file_path)
    print("return type -",type(result))
    print("Cleaned Code:")
    print(result["cleaned_code"])

    print("\nFunction Definitions:")
    for func_name, func_code in result["function_definitions"]:
        print(f"Function: {func_name}")
        print(func_code)

    print("\nFunction Calls:")
    for call_name, call_code in result["function_calls"]:
        print(f"Function Call: {call_name}")
        print(call_code)

    print("\nExternal Dependencies (Imports):")
    for import_code in result["external_dependencies"]:
        print(import_code)
