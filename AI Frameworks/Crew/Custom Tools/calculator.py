import math
from enum import Enum

from langchain_core.tools import tool
from pydantic import BaseModel, Field, field_validator

OPERATIONS = {"add", "sub", "mul", "div", "pow", "sqrt", "mod"}


@tool
def calculate_v1(expression: str) -> float:
    """Evaluate a mathematical expression string.

    Use eval to compute the result. Accepts any valid Python math expression.

    Args:
        expression: Math expression as string (e.g. "2 + 2", "3 * 7").

    Returns:
        Evaluated result as float.
    """
    allowed = set("0123456789+-*/.()% ")
    if not all(c in allowed for c in expression):
        raise ValueError("Expression contains disallowed characters")
    return float(eval(expression))


_OP_ALIASES = {"divide": "div", "multiply": "mul", "subtract": "sub", "addition": "add"}


@tool
def calculate_v2(*, a: float, b: float = 0.0, op: str = "add") -> float:
    """Basic arithmetic with two numbers.

    Args:
        a: First number.
        b: Second number (default 0).
        op: Operator: add, sub, mul, div, pow (default add).

    Returns:
        Computed result.
    """
    op = _OP_ALIASES.get(op, op)
    if op == "add":
        return a + b
    if op == "sub":
        return a - b
    if op == "mul":
        return a * b
    if op == "div":
        if b == 0:
            raise ValueError("Division by zero")
        return a / b
    if op == "pow":
        return a ** b
    raise ValueError(f"Unknown operator: {op}")


@tool
def calculate_v3(*, a: float, b: float = 0.0, op: str = "add") -> float:
    """Perform arithmetic operations between two numbers.

    Use this tool when the user asks to:
    - Add, subtract, multiply, divide, or exponentiate numbers
    - Perform math calculations or basic arithmetic
    - Compute sums, differences, products, quotients

    Supported operators:
    - add: a + b (b defaults to 0 if omitted)
    - sub: a - b (b defaults to 0 if omitted)
    - mul: a * b (b defaults to 1 if omitted)
    - div: a / b (raises error if b is 0)
    - pow: a raised to power b

    Args:
        a: First operand.
        b: Second operand (default 0 for add/sub, 1 for mul/div, 2 for pow).
        op: Operation name: add, sub, mul, div, pow.

    Returns:
        Computed numeric result.
    """
    op = _OP_ALIASES.get(op, op)
    _b = b
    if op in ("mul", "div") and b == 0.0:
        _b = 1.0
    if op == "pow" and b == 0.0:
        _b = 2.0
    if op == "add":
        return a + _b
    if op == "sub":
        return a - _b
    if op == "mul":
        return a * _b
    if op == "div":
        if _b == 0:
            raise ValueError("Division by zero")
        return a / _b
    if op == "pow":
        return a ** _b
    raise ValueError(f"Unknown operator: {op}")


class OpEnum(str, Enum):
    add = "add"
    sub = "sub"
    mul = "mul"
    div = "div"
    pow = "pow"
    sqrt = "sqrt"
    mod = "mod"


class CalcInput(BaseModel):
    a: float = Field(description="First operand")
    b: float = Field(default=0.0, description="Second operand")
    op: OpEnum = Field(default=OpEnum.add, description="Operation to perform")

    @field_validator("op", mode="before")
    @classmethod
    def normalize_op(cls, v):
        if isinstance(v, str):
            return {"divide": "div", "multiply": "mul", "subtract": "sub", "addition": "add"}.get(v, v)
        return v

    @field_validator("b")
    @classmethod
    def check_div_zero(cls, v, info):
        if info.data.get("op") == OpEnum.div and v == 0:
            raise ValueError("Division by zero is not allowed")
        return v


@tool(args_schema=CalcInput)
def calculate_v4(*, a: float, b: float = 0.0, op: str = "add") -> float:
    """Perform arithmetic using validated parameters.

    Supported operations: add, sub, mul, div, pow, sqrt, mod.
    Input validation via Pydantic schema with field descriptions.

    Args:
        a: First operand.
        b: Second operand (not used for sqrt).
        op: Operation name.

    Returns:
        Computed result.
    """
    if op == "add":
        return a + b
    if op == "sub":
        return a - b
    if op == "mul":
        return a * b
    if op == "div":
        return a / b
    if op == "pow":
        return a ** b
    if op == "sqrt":
        return math.sqrt(a)
    if op == "mod":
        return a % b
    raise ValueError(f"Unknown operator: {op}")


@tool
def calculate_v5(
    expression: str,
    *,
    precision: int = 6,
    safe_mode: bool = True,
) -> float:
    """Evaluate a math expression with safety and precision options.

    Args:
        expression: Math expression as string.
        precision: Decimal places to round result (default 6).
        safe_mode: If True, restrict to basic arithmetic only (default True).

    Returns:
        Evaluated result rounded to precision.
    """
    if safe_mode:
        allowed = set("0123456789+-*/.()% ")
        if not all(c in allowed for c in expression):
            raise ValueError("Expression contains disallowed characters")
    result = float(eval(expression))
    return round(result, precision)


OP_MAP = {
    "add": lambda a, b: a + b,
    "sub": lambda a, b: a - b,
    "mul": lambda a, b: a * b,
    "multiply": lambda a, b: a * b,
    "div": lambda a, b: a / b if b != 0 else (_ for _ in ()).throw(ValueError("division by zero")),
    "pow": lambda a, b: a ** b,
    "sqrt": lambda a, _: math.sqrt(a),
    "mod": lambda a, b: a % b,
}


@tool
def calculate_safe(*, a: float = 0.0, b: float = 0.0, op: str = "add") -> str:
    """Perform arithmetic with full input validation.

    Validates operator, handles division by zero, supports all ops.
    Returns descriptive error messages instead of crashing.

    Args:
        a: First operand.
        b: Second operand.
        op: Operation: add, sub, mul, div, pow, sqrt, mod.

    Returns:
        Result string or error description.
    """
    if op not in OP_MAP:
        valid = ", ".join(sorted(OP_MAP))
        return f"Error: unknown operator '{op}'. Valid: {valid}"

    if op == "div" and b == 0:
        return "Error: division by zero is not allowed"

    if op == "sqrt" and a < 0:
        return "Error: cannot compute sqrt of negative number"

    try:
        result = OP_MAP[op](a, b)
        rounded = round(result, 6)
        return str(int(rounded)) if isinstance(rounded, float) and rounded == int(rounded) else str(rounded)
    except Exception as e:
        return f"Error: {e}"

