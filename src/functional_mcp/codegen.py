"""
Code generation from tool schemas.

Generates Python type definitions (Pydantic, dataclass) or TypeScript
from MCP tool input/output schemas.
"""

from typing import Any


def generate_types_file(
    schemas: list[dict[str, Any]],
    format: str = "pydantic",
    only: str | None = None,
) -> str:
    """
    Generate type definitions file from tool schemas.
    
    Args:
        schemas: List of tool schema dicts with name, description, input_schema
        format: 'pydantic', 'dataclass', or 'typescript'
        only: Generate only 'input', 'output', or None for both
    
    Returns:
        Generated code as string
    """
    if format == "pydantic":
        return _generate_pydantic(schemas, only)
    elif format == "dataclass":
        return _generate_dataclass(schemas, only)
    elif format == "typescript":
        return _generate_typescript(schemas, only)
    else:
        raise ValueError(f"Unknown format: {format}. Use 'pydantic', 'dataclass', or 'typescript'")


def _generate_pydantic(schemas: list[dict[str, Any]], only: str | None) -> str:
    """Generate Pydantic models from schemas."""
    lines = [
        "# Auto-generated types from MCP server",
        "# DO NOT EDIT - regenerate with tools.generateTypes()",
        "",
        "from pydantic import BaseModel, Field",
        "from typing import Optional, Any",
        "from datetime import datetime",
        "from uuid import UUID",
        "",
    ]
    
    for schema in schemas:
        tool_name = schema["name"]
        description = schema.get("description")
        input_schema = schema["input_schema"]
        
        # Generate input class if needed
        if only is None or only == "input":
            class_name = _to_pascal_case(tool_name) + "Input"
            
            lines.append(f"class {class_name}(BaseModel):")
            
            # Add docstring
            if description:
                lines.append(f'    """{description}"""')
                lines.append("")
            
            # Parse properties
            properties = input_schema.get("properties", {})
            required = set(input_schema.get("required", []))
            
            if not properties:
                lines.append("    pass")
            else:
                for prop_name, prop_schema in properties.items():
                    python_type = _json_type_to_python(prop_schema)
                    prop_desc = prop_schema.get("description", "")
                    
                    # Determine if optional
                    is_required = prop_name in required
                    if not is_required:
                        python_type = f"Optional[{python_type}]"
                    
                    # Get default
                    if "default" in prop_schema:
                        default_val = repr(prop_schema["default"])
                        field_str = f"Field(default={default_val}"
                    elif not is_required:
                        field_str = f"Field(default=None"
                    else:
                        field_str = "Field("
                    
                    # Add description
                    if prop_desc:
                        field_str += f', description="{prop_desc}"'
                    
                    field_str += ")"
                    
                    lines.append(f"    {prop_name}: {python_type} = {field_str}")
            
            lines.append("")
            lines.append("")
    
    return "\n".join(lines)


def _generate_dataclass(schemas: list[dict[str, Any]], only: str | None) -> str:
    """Generate dataclasses from schemas."""
    lines = [
        "# Auto-generated types from MCP server",
        "# DO NOT EDIT - regenerate with tools.generateTypes()",
        "",
        "from dataclasses import dataclass, field",
        "from typing import Optional, Any",
        "from datetime import datetime",
        "from uuid import UUID",
        "",
    ]
    
    for schema in schemas:
        tool_name = schema["name"]
        description = schema.get("description")
        input_schema = schema["input_schema"]
        
        if only is None or only == "input":
            class_name = _to_pascal_case(tool_name) + "Input"
            
            lines.append("@dataclass")
            lines.append(f"class {class_name}:")
            
            if description:
                lines.append(f'    """{description}"""')
                lines.append("")
            
            properties = input_schema.get("properties", {})
            required = set(input_schema.get("required", []))
            
            if not properties:
                lines.append("    pass")
            else:
                for prop_name, prop_schema in properties.items():
                    python_type = _json_type_to_python(prop_schema)
                    is_required = prop_name in required
                    
                    if not is_required:
                        python_type = f"Optional[{python_type}]"
                    
                    if "default" in prop_schema:
                        default_val = repr(prop_schema["default"])
                        lines.append(f"    {prop_name}: {python_type} = {default_val}")
                    elif not is_required:
                        lines.append(f"    {prop_name}: {python_type} = None")
                    else:
                        lines.append(f"    {prop_name}: {python_type}")
            
            lines.append("")
            lines.append("")
    
    return "\n".join(lines)


def _generate_typescript(schemas: list[dict[str, Any]], only: str | None) -> str:
    """Generate TypeScript interfaces from schemas."""
    lines = [
        "// Auto-generated types from MCP server",
        "// DO NOT EDIT - regenerate with tools.generateTypes()",
        "",
    ]
    
    for schema in schemas:
        tool_name = schema["name"]
        description = schema.get("description")
        input_schema = schema["input_schema"]
        
        if only is None or only == "input":
            interface_name = _to_pascal_case(tool_name) + "Input"
            
            if description:
                lines.append(f"/** {description} */")
            
            lines.append(f"export interface {interface_name} {{")
            
            properties = input_schema.get("properties", {})
            required = set(input_schema.get("required", []))
            
            for prop_name, prop_schema in properties.items():
                ts_type = _json_type_to_typescript(prop_schema)
                prop_desc = prop_schema.get("description", "")
                is_required = prop_name in required
                
                if prop_desc:
                    lines.append(f"  /** {prop_desc} */")
                
                optional_marker = "" if is_required else "?"
                lines.append(f"  {prop_name}{optional_marker}: {ts_type};")
            
            lines.append("}")
            lines.append("")
    
    return "\n".join(lines)


def _to_pascal_case(name: str) -> str:
    """Convert snake_case or kebab-case to PascalCase."""
    parts = name.replace("-", "_").split("_")
    return "".join(word.capitalize() for word in parts)


def _json_type_to_python(schema: dict[str, Any]) -> str:
    """Convert JSON Schema type to Python type hint."""
    json_type = schema.get("type", "string")
    
    if json_type == "string":
        # Check for format hints
        if schema.get("format") == "date-time":
            return "datetime"
        elif schema.get("format") == "uuid":
            return "UUID"
        return "str"
    elif json_type == "number":
        return "float"
    elif json_type == "integer":
        return "int"
    elif json_type == "boolean":
        return "bool"
    elif json_type == "array":
        items = schema.get("items", {})
        item_type = _json_type_to_python(items)
        return f"list[{item_type}]"
    elif json_type == "object":
        return "dict[str, Any]"
    else:
        return "Any"


def _json_type_to_typescript(schema: dict[str, Any]) -> str:
    """Convert JSON Schema type to TypeScript type."""
    json_type = schema.get("type", "string")
    
    if json_type == "string":
        return "string"
    elif json_type in ["number", "integer"]:
        return "number"
    elif json_type == "boolean":
        return "boolean"
    elif json_type == "array":
        items = schema.get("items", {})
        item_type = _json_type_to_typescript(items)
        return f"{item_type}[]"
    elif json_type == "object":
        return "Record<string, any>"
    else:
        return "any"


__all__ = ["generate_types_file"]

