import math
import json
from datetime import datetime

# -----------------------------------------------------------
# TOOL 1: Calculator
# -----------------------------------------------------------

def calculate(expression: str) -> dict:
    """
    Evaluates a safe mathematical expression and returns the result.
    Use this when the user asks to compute, calculate, or evaluate 
    any arithmetic expression. 
    
    Args:
        expression: A mathematical expression as a string.
    Returns:
        A dict with 'result' (float) or 'error' (str).
    """
    try:
        # Restrict eval to math functions only; never use exec
        allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        allowed["__builtins__"] = {}
        
        result = eval(expression, allowed)  # noqa: S307
        return {"result": float(result), "expression": expression}
    except Exception as e:
        return {"error": str(e), "expression": expression}

# -----------------------------------------------------------
# TOOL 2: Unit Converter
# -----------------------------------------------------------

def convert_units(value: float, from_unit: str, to_unit: str) -> dict:
    """
    Converts a value between physical units (length, weight, temperature).
    Do NOT use for currency conversion.

    Args:
        value: The numeric value to convert.
        from_unit: The source unit (e.g., 'km', 'kg', 'celsius').
        to_unit: The target unit (e.g., 'miles', 'lbs', 'fahrenheit').
    Returns:
        A dict with 'result' (float) and 'unit' (str).
    """
    conversions = {
        ("km", "miles"): lambda x: x * 0.621371,
        ("miles", "km"): lambda x: x * 1.60934,
        ("kg", "lbs"): lambda x: x * 2.20462,
        ("lbs", "kg"): lambda x: x * 0.453592,
        ("celsius", "fahrenheit"): lambda x: (x * 9 / 5) + 32,
        ("fahrenheit", "celsius"): lambda x: (x - 32) * 5 / 9,
        ("meters", "feet"): lambda x: x * 3.28084,
        ("feet", "meters"): lambda x: x * 0.3048,
    }

    key = (from_unit.lower(), to_unit.lower())
    if key in conversions:
        return {
            "result": round(conversions[key](value), 4),
            "unit": to_unit,
            "original": f"{value} {from_unit}",
        }
    return {"error": f"Conversion from {from_unit} to {to_unit} is not supported."}

# -----------------------------------------------------------
# TOOL 3: Timestamp Formatter
# -----------------------------------------------------------

def format_timestamp(unix_timestamp: int, timezone_offset_hours: float = 0.0) -> dict:
    """
    Converts a Unix timestamp to a human-readable date and time string.
    
    Args:
        unix_timestamp: Seconds since Unix epoch (integer).
        timezone_offset_hours: UTC offset in hours, e.g., 1.0 for WAT (Lagos).
    Returns:
        A dict with 'formatted' (str), 'utc' (str), and 'local' (str).
    """
    try:
        utc_dt = datetime.utcfromtimestamp(unix_timestamp)
        offset_seconds = int(timezone_offset_hours * 3600)
        local_dt = datetime.utcfromtimestamp(unix_timestamp + offset_seconds)
        
        return {
            "utc": utc_dt.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "local": local_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "offset": f"UTC+{timezone_offset_hours}",
            "formatted": local_dt.strftime("%A, %d %B %Y at %H:%M"),
        }
    except (OSError, OverflowError, ValueError) as e:
        return {"error": str(e), "unix_timestamp": unix_timestamp}