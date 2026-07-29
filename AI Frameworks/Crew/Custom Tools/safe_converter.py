from langchain_core.tools import tool

from crew_tools.unit_converter import LENGTH, TEMPERATURE, WEIGHT
from crew_tools.validation import validate_in, validate_positive

ALL_CATEGORIES = {"length", "weight", "temperature"}
ALL_UNITS = {*LENGTH, *WEIGHT, *TEMPERATURE}
CATEGORY_UNITS = {
    "length": {*LENGTH},
    "weight": {*WEIGHT},
    "temperature": {*TEMPERATURE},
}


def _safe_convert(value, from_unit, to_unit, category):
    try:
        value = validate_positive(value, "value")
    except ValueError:
        return f"Error: value must be positive, got {value}"

    try:
        validate_in(category, ALL_CATEGORIES, "category")
    except ValueError as e:
        return f"Error: {e}"

    valid_units = CATEGORY_UNITS.get(category, set())
    try:
        validate_in(from_unit, valid_units, "from_unit")
    except ValueError as e:
        return f"Error (from_unit): {e}"

    try:
        validate_in(to_unit, valid_units, "to_unit")
    except ValueError as e:
        return f"Error (to_unit): {e}"

    if category == "length":
        result = value * LENGTH[from_unit] / LENGTH[to_unit]
    elif category == "weight":
        result = value * WEIGHT[from_unit] / WEIGHT[to_unit]
    elif category == "temperature":
        result = _safe_temperature(value, from_unit, to_unit)
    else:
        return f"Error: unknown category '{category}'"

    return f"{round(result, 6)}"


def _safe_temperature(value, from_unit, to_unit):
    if from_unit == to_unit:
        return value
    if from_unit == "celsius":
        if to_unit == "fahrenheit":
            return value * 9 / 5 + 32
        return value + 273.15
    if from_unit == "fahrenheit":
        if to_unit == "celsius":
            return (value - 32) * 5 / 9
        return (value - 32) * 5 / 9 + 273.15
    if from_unit == "kelvin":
        if to_unit == "celsius":
            return value - 273.15
        return (value - 273.15) * 9 / 5 + 32
    return value


@tool
def convert_safe(value, from_unit, to_unit, category="length"):
    """Convert units with full input validation.

    Validates:
    - value is positive number
    - from_unit/to_unit are valid for the category
    - category is length/weight/temperature

    Returns result string or descriptive error message.

    Args:
        value: Positive numeric value.
        from_unit: Source unit.
        to_unit: Target unit.
        category: Measurement category.

    Returns:
        Converted value or error message.
    """
    return _safe_convert(value, from_unit, to_unit, category)
