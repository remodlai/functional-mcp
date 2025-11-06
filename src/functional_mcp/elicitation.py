"""
User input elicitation handler.

When MCP servers request user input, this module handles
terminal prompts with type-aware formatting.
"""

from typing import Any, Callable
import json


def create_elicitation_handler() -> Callable:
    """
    Create default terminal elicitation handler.
    
    Returns:
        Elicitation handler function
    """
    
    async def elicitation_handler(
        message: str,
        schema: dict[str, Any],
    ) -> Any:
        """
        Handle user input request from MCP server.
        
        Args:
            message: Prompt message for user
            schema: JSON schema describing expected input
        
        Returns:
            User input in appropriate type
        """
        print(f"\n🔔 Server Request: {message}")
        print("=" * 60)
        
        schema_type = schema.get("type", "string")
        
        # String input
        if schema_type == "string":
            return input("→ ")
        
        # Boolean input
        elif schema_type == "boolean":
            response = input("→ (y/n): ").lower()
            return response in ["y", "yes", "true", "1"]
        
        # Number input
        elif schema_type in ["number", "integer"]:
            try:
                value = input("→ ")
                return int(value) if schema_type == "integer" else float(value)
            except ValueError:
                print("Invalid number, using 0")
                return 0
        
        # Object input (JSON)
        elif schema_type == "object":
            properties = schema.get("properties", {})
            result = {}
            
            print("\nEnter values for each field:")
            for prop_name, prop_schema in properties.items():
                prop_desc = prop_schema.get("description", "")
                prompt = f"  {prop_name}"
                if prop_desc:
                    prompt += f" ({prop_desc})"
                prompt += ": "
                
                value = input(prompt)
                
                # Type conversion
                prop_type = prop_schema.get("type", "string")
                if prop_type == "boolean":
                    result[prop_name] = value.lower() in ["y", "yes", "true", "1"]
                elif prop_type in ["number", "integer"]:
                    try:
                        result[prop_name] = int(value) if prop_type == "integer" else float(value)
                    except ValueError:
                        result[prop_name] = value
                else:
                    result[prop_name] = value
            
            return result
        
        # Array input (JSON)
        elif schema_type == "array":
            try:
                value = input("→ (JSON array): ")
                return json.loads(value)
            except json.JSONDecodeError:
                print("Invalid JSON, returning empty array")
                return []
        
        # Fallback: JSON input
        else:
            try:
                value = input("→ (JSON): ")
                return json.loads(value)
            except json.JSONDecodeError:
                return value
    
    return elicitation_handler


class ElicitationDefaults:
    """
    Pre-filled answers for automated scripts.
    
    Example:
        defaults = ElicitationDefaults({
            "confirm_booking": True,
            "seat_preference": "window"
        })
    """
    
    def __init__(self, defaults: dict[str, Any]):
        self.defaults = defaults
    
    async def __call__(self, message: str, schema: dict[str, Any]) -> Any:
        """Return pre-filled value if available."""
        # Extract field name from message (heuristic)
        field_name = message.split(":")[-1].strip().lower().replace(" ", "_")
        
        if field_name in self.defaults:
            return self.defaults[field_name]
        
        # Fallback to default elicitation
        handler = create_elicitation_handler()
        return await handler(message, schema)


__all__ = ["create_elicitation_handler", "ElicitationDefaults"]

