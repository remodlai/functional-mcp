"""
Example: Generate type definitions from MCP tools.

Shows how to create typed interfaces for tools.
"""

from functional_mcp import load_server


# Load a server
server = load_server("npx weather-server")

# Get tools
tools = server.tools

print("Generating Types")
print("=" * 60)

# Generate Pydantic models
pydantic_path = tools.generateTypes(
    path='./types/weather_pydantic.py',
    format='pydantic',
    only='input',
    with_instructions=True
)

print(f"✅ Generated Pydantic types: {pydantic_path}")

# Generate dataclasses
dataclass_path = tools.generateTypes(
    path='./types/weather_dataclass.py',
    format='dataclass',
    only='input',
    with_instructions=True
)

print(f"✅ Generated dataclass types: {dataclass_path}")

# Generate TypeScript
ts_path = tools.generateTypes(
    path='./types/weather.ts',
    format='typescript',
    only='input',
    with_instructions=True
)

print(f"✅ Generated TypeScript types: {ts_path}")


# Now use the generated types
print("\nUsing Generated Types")
print("=" * 60)

# Import generated Pydantic model
import sys
sys.path.insert(0, './types')

from weather_pydantic import GetForecastInput

# Create typed input
forecast_input = GetForecastInput(
    lat=25.7617,
    lon=-80.1918,
    units="imperial"
)

# IDE has full autocomplete!
# Validation happens automatically via Pydantic

# Call tool with validated input
result = server.get_forecast(**forecast_input.model_dump())
print(f"Weather: {result}")

server.close()


print("\nGenerated Pydantic Model Example:")
print("=" * 60)
print("""
# weather_pydantic.py (auto-generated)

from pydantic import BaseModel, Field
from typing import Optional

class GetForecastInput(BaseModel):
    '''Get weather forecast for a location.'''
    
    lat: float = Field(description='Latitude coordinate')
    lon: float = Field(description='Longitude coordinate')
    units: Optional[str] = Field(default='metric', description='Temperature units')
    detail_level: Optional[int] = Field(default=1, description='Forecast detail level')
""")

