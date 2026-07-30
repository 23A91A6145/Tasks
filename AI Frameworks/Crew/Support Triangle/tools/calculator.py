import ast

from crewai.tools import tool

from config.settings import CALCULATOR_MAX_NESTING


def _check_depth(node, depth=0):
    if depth > CALCULATOR_MAX_NESTING:
        raise RecursionError(f"Expression exceeds maximum nesting depth ({CALCULATOR_MAX_NESTING})")
    if isinstance(node, ast.BinOp):
        _check_depth(node.left, depth + 1)
        _check_depth(node.right, depth + 1)
    elif isinstance(node, ast.UnaryOp):
        _check_depth(node.operand, depth + 1)


def _eval_node(node):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.UnaryOp):
        op = node.op
        val = _eval_node(node.operand)
        if isinstance(op, ast.UAdd):
            return +val
        if isinstance(op, ast.USub):
            return -val
    if isinstance(node, ast.BinOp):
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        op = node.op
        if isinstance(op, ast.Add):
            return left + right
        if isinstance(op, ast.Sub):
            return left - right
        if isinstance(op, ast.Mult):
            return left * right
        if isinstance(op, ast.Div):
            return left / right
        if isinstance(op, ast.FloorDiv):
            return left // right
        if isinstance(op, ast.Mod):
            return left % right
        if isinstance(op, ast.Pow):
            return left ** right
    raise ValueError(f"Unsupported expression: {type(node).__name__}")


@tool("Calculator")
def calculator_tool(expression: str) -> str:
    """Evaluate a mathematical expression safely. Supports +, -, *, /, //, %, **, and parentheses."""
    if not expression.strip():
        return "Error: empty expression"
    try:
        tree = ast.parse(expression.strip(), mode="eval")
        _check_depth(tree)
        result = _eval_node(tree.body)
        if isinstance(result, float):
            return f"{result:.4f}".rstrip("0").rstrip(".")
        return str(result)
    except RecursionError as e:
        return f"Error: {e}"
    except (SyntaxError, ValueError, ZeroDivisionError) as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Calculation error: {e}"
