"""
Python file-based skill to compute numbers.
"""

SKILL_METADATA = {
    "name": "math_factorial",
    "description": "Calculates the factorial of a positive integer.",
    "version": "1.0.1",
    "parameters": {
        "n": {"type": "integer", "description": "The number to compute factorial for"}
    }
}

def execute(n: int) -> int:
    import math
    try:
        val = int(n)
        return math.factorial(val)
    except Exception as e:
        raise ValueError(f"Invalid input to factorial: {e}")
