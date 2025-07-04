import os
import ast

def extract_docstrings_from_file(file_path):
    """
    Extracts the module docstring and all function docstrings defined in the file.
    Returns a dict: {'module_doc': str, 'functions': {func_name: docstring}}
    """
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    docstrings = {
        "module_doc": ast.get_docstring(tree),
        "functions": {}
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            docstrings["functions"][node.name] = ast.get_docstring(node) or "No docstring."

    return docstrings

def scan_directory_for_docs(directory="."):
    """
    Scans .py files in the directory and extracts docstrings.
    Returns dict: {module_name: docstrings_dict}
    """
    docs = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                module_name = os.path.relpath(path, directory).replace(os.sep, ".")[:-3]  # remove .py
                docs[module_name] = extract_docstrings_from_file(path)
    return docs

def generate_markdown_docs(docs_dict, output_file="DOCUMENTATION.md"):
    """
    Generates a Markdown file with the documentation.
    """
    lines = ["# Automatic Documentation\n"]

    for module, content in docs_dict.items():
        lines.append(f"## Module `{module}`\n")
        mod_doc = content.get("module_doc") or "No docstring."
        lines.append(f"{mod_doc}\n")

        funcs = content.get("functions", {})
        if funcs:
            lines.append("### Functions:\n")
            for func_name, func_doc in funcs.items():
                lines.append(f"- **{func_name}**: {func_doc}\n")
        else:
            lines.append("_No functions found._\n")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✅ Documentation generated in {output_file}")
