import ast


def analyze_code_structure(code):

    try:

        tree = ast.parse(code)

        result = {
            "functions": [],
            "classes": [],
            "imports": [],
            "loops": 0,
            "ifs": 0,
            "returns": 0
        }

        for node in ast.walk(tree):

            if isinstance(node, ast.FunctionDef):
                result["functions"].append(node.name)

            elif isinstance(node, ast.ClassDef):
                result["classes"].append(node.name)

            elif isinstance(node, ast.Import):
                for name in node.names:
                    result["imports"].append(name.name)

            elif isinstance(node, ast.ImportFrom):
                result["imports"].append(node.module)

            elif isinstance(node, ast.For):
                result["loops"] += 1

            elif isinstance(node, ast.While):
                result["loops"] += 1

            elif isinstance(node, ast.If):
                result["ifs"] += 1

            elif isinstance(node, ast.Return):
                result["returns"] += 1

        return result

    except Exception as e:

        return {
            "error": str(e)
        }