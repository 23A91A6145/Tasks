from enum import Enum

from langchain_core.tools import tool
from pydantic import BaseModel, Field, field_validator

LENGTH = {
    "mm": 0.001, "cm": 0.01, "m": 1.0, "km": 1000.0,
    "in": 0.0254, "ft": 0.3048, "yd": 0.9144, "mi": 1609.344,
}

WEIGHT = {
    "mg": 0.001, "g": 1.0, "kg": 1000.0, "t": 1_000_000.0,
    "oz": 28.3495, "lb": 453.592,
}

TEMPERATURE = {"celsius", "fahrenheit", "kelvin"}


def _convert_length(value, from_unit, to_unit):
    return value * LENGTH[from_unit] / LENGTH[to_unit]


def _convert_weight(value, from_unit, to_unit):
    return value * WEIGHT[from_unit] / WEIGHT[to_unit]


def _convert_temperature(value, from_unit, to_unit):
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
def convert_v1(
    value: float, from_unit: str, to_unit: str, category: str = "length"
) -> float:
    """Convert units between different measurement systems.

    Supports length (mm, cm, m, km, in, ft, yd, mi),
    weight (mg, g, kg, t, oz, lb),
    and temperature (celsius, fahrenheit, kelvin).

    Args:
        value: Numeric value to convert.
        from_unit: Source unit.
        to_unit: Target unit.
        category: Measurement category (length, weight, temperature).

    Returns:
        Converted value.
    """
    if category == "length":
        return _convert_length(value, from_unit, to_unit)
    if category == "weight":
        return _convert_weight(value, from_unit, to_unit)
    if category == "temperature":
        return _convert_temperature(value, from_unit, to_unit)
    raise ValueError(f"Unknown category: {category}")


@tool
def convert_v2(
    value: float, from_unit: str, to_unit: str, category: str = "length"
) -> float:
    """Convert a value from one unit to another.

    Supports length, weight, and temperature categories.

    Args:
        value: The numeric value to convert.
        from_unit: The unit to convert from (e.g. km, kg, celsius).
        to_unit: The unit to convert to (e.g. m, lb, fahrenheit).
        category: Type of measurement: length, weight, or temperature.

    Returns:
        The converted numeric value.
    """
    if category == "length":
        return _convert_length(value, from_unit, to_unit)
    if category == "weight":
        return _convert_weight(value, from_unit, to_unit)
    if category == "temperature":
        return _convert_temperature(value, from_unit, to_unit)
    raise ValueError(f"Unknown category: {category}")


@tool
def convert_v3(
    value: float, from_unit: str, to_unit: str, category: str = "length"
) -> float:
    """Convert a numeric value between different measurement units.

    Use this tool whenever the user asks to:
    - Convert length: km to miles, cm to inches, meters to feet
    - Convert weight: kg to pounds, grams to ounces, tons to kg
    - Convert temperature: Celsius to Fahrenheit, Kelvin to Celsius
    - Unit conversion, measurement conversion, metric to imperial
    - Distance, mass, or temperature conversion

    Supported categories:
    - length: mm, cm, m, km, in, ft, yd, mi
    - weight: mg, g, kg, t, oz, lb
    - temperature: celsius, fahrenheit, kelvin

    Args:
        value: The numeric value to convert.
        from_unit: Source unit abbreviation (e.g. km, kg, celsius).
        to_unit: Target unit abbreviation (e.g. mi, lb, fahrenheit).
        category: Measurement category (length, weight, temperature).

    Returns:
        Converted numeric value rounded to 6 decimal places.
    """
    if category == "length":
        return round(_convert_length(value, from_unit, to_unit), 6)
    if category == "weight":
        return round(_convert_weight(value, from_unit, to_unit), 6)
    if category == "temperature":
        return round(_convert_temperature(value, from_unit, to_unit), 6)
    raise ValueError(f"Unknown category: {category}")


class CategoryEnum(str, Enum):
    length = "length"
    weight = "weight"
    temperature = "temperature"


class ConvertInput(BaseModel):
    value: float = Field(gt=0, description="Numeric value to convert (must be positive)")
    from_unit: str = Field(min_length=1, description="Source unit (e.g. km, kg, celsius)")
    to_unit: str = Field(min_length=1, description="Target unit (e.g. mi, lb, fahrenheit)")
    category: CategoryEnum = Field(default=CategoryEnum.length, description="Measurement category")

    @field_validator("from_unit")
    @classmethod
    def from_unit_lower(cls, v):
        return v.lower()

    @field_validator("to_unit")
    @classmethod
    def to_unit_lower(cls, v):
        return v.lower()


@tool(args_schema=ConvertInput)
def convert_v4(
    value: float,
    from_unit: str,
    to_unit: str,
    category: str = "length",
) -> float:
    """Convert units with Pydantic-validated parameters.

    Supports length (mm, cm, m, km, in, ft, yd, mi),
    weight (mg, g, kg, t, oz, lb),
    temperature (celsius, fahrenheit, kelvin).

    Validation:
    - value must be positive (>0)
    - category restricted to length, weight, temperature
    - unit names auto-lowered

    Args:
        value: Positive numeric value to convert.
        from_unit: Source unit abbreviation.
        to_unit: Target unit abbreviation.
        category: Measurement category.

    Returns:
        Converted value rounded to 6 places.
    """
    if category == "length":
        return round(_convert_length(value, from_unit, to_unit), 6)
    if category == "weight":
        return round(_convert_weight(value, from_unit, to_unit), 6)
    if category == "temperature":
        return round(_convert_temperature(value, from_unit, to_unit), 6)
    raise ValueError(f"Unknown category: {category}")
