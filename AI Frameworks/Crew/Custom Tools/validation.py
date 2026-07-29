def validate_positive(value, name="value"):
    if value is None:
        raise ValueError(f"{name} cannot be None")
    if not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number, got {type(value).__name__}")
    if value <= 0:
        raise ValueError(f"{name} must be positive, got {value}")
    return float(value)


def validate_non_empty(text, name="text"):
    if text is None:
        raise ValueError(f"{name} cannot be None")
    if not isinstance(text, str):
        raise TypeError(f"{name} must be a string, got {type(text).__name__}")
    if not text.strip():
        raise ValueError(f"{name} cannot be empty or whitespace-only")
    return text


def validate_in(value, options, name="value"):
    if value not in options:
        opts = ", ".join(sorted(options))
        raise ValueError(f"{name} must be one of: {opts}. Got: {value}")
    return value


def validate_range(value, min_v=None, max_v=None, name="value"):
    if min_v is not None and value < min_v:
        raise ValueError(f"{name} must be >= {min_v}, got {value}")
    if max_v is not None and value > max_v:
        raise ValueError(f"{name} must be <= {max_v}, got {value}")
    return value


def safe_call(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        return {"error": str(e), "success": False}


def safe_result(value=None, error=None):
    if error:
        return {"success": False, "error": str(error), "result": None}
    return {"success": True, "error": None, "result": value}
