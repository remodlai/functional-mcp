"""
JSON Schema → Python type conversion.

Handles type mapping for tool arguments and return values.
"""

from typing import Any, get_origin, get_args


def json_schema_to_python_type(schema: dict[str, Any]) -> type:
    """
    Convert JSON Schema type to Python type.
    
    Args:
        schema: JSON Schema definition
    
    Returns:
        Python type
    
    Example:
        >>> json_schema_to_python_type({"type": "string"})
        <class 'str'>
        >>> json_schema_to_python_type({"type": "array", "items": {"type": "string"}})
        list[str]
    """
    schema_type = schema.get("type")
    
    if schema_type == "string":
        return str
    elif schema_type == "number":
        return float
    elif schema_type == "integer":
        return int
    elif schema_type == "boolean":
        return bool
    elif schema_type == "array":
        items_schema = schema.get("items", {})
        item_type = json_schema_to_python_type(items_schema)
        return list[item_type]  # type: ignore
    elif schema_type == "object":
        return dict[str, Any]
    elif schema_type == "null":
        return type(None)
    else:
        # Unknown or complex type
        return Any


def python_type_to_json_schema(py_type: type) -> dict[str, Any]:
    """
    Convert Python type to JSON Schema.
    
    Args:
        py_type: Python type
    
    Returns:
        JSON Schema definition
    """
    origin = get_origin(py_type)
    
    # Handle generic types (list, dict, etc.)
    if origin is list:
        args = get_args(py_type)
        if args:
            return {
                "type": "array",
                "items": python_type_to_json_schema(args[0])
            }
        return {"type": "array"}
    
    elif origin is dict:
        return {"type": "object"}
    
    # Handle basic types
    elif py_type is str:
        return {"type": "string"}
    elif py_type is int:
        return {"type": "integer"}
    elif py_type is float:
        return {"type": "number"}
    elif py_type is bool:
        return {"type": "boolean"}
    elif py_type is type(None):
        return {"type": "null"}
    else:
        # Unknown type
        return {"type": "object"}


__all__ = ["json_schema_to_python_type", "python_type_to_json_schema"]

