# functional-mcp

**Every MCP server is a Python module. Automatically.**

```python
from functional_mcp import load_server

# Any MCP server → Python
server = load_server("npx -y @modelcontextprotocol/server-filesystem /tmp")

# Call tools
files = server.list_directory(path="/tmp")

# Or access with metadata
list_tool = server.tools.list_directory
print(list_tool.schema.toDict())  # See what it needs
files = list_tool(path="/tmp")
```

No learning. No setup. Full transparency.

---

## What Is This?

MCP servers expose tools, resources, and prompts in a standard format.

**functional-mcp translates that into Python.**

Instantly.

```python
from functional_mcp import load_server

server = load_server("npx your-mcp-server")

# Tools → callable objects with metadata
search = server.tools.search
print(search.name)          # "search"
print(search.description)   # "Search for items..."
print(search.schema.toDict())  # Full schema as dict

# Call and get hydrated Python objects (not just JSON!)
result = search(query="test")
# ↑ Returns real Python types:
#   - datetime objects (not ISO strings)
#   - UUID objects (not string IDs)  
#   - Pydantic models (not dicts)
#   - Primitives unwrapped (8 not {"result": 8})

# Resources → attributes
config = server.CONFIG  # Static resource

# Prompts → template functions
prompt = server.format_prompt(style="formal")
```

**Every tool is first-class. Hydrated objects. Full transparency.**

---

## The Magic

### Before

**Step 1:** Find MCP server  
**Step 2:** Read MCP documentation  
**Step 3:** Learn the protocol  
**Step 4:** Write integration code  
**Step 5:** Handle edge cases  
**Step 6:** Maybe it works

### After

```python
from functional_mcp import load_server
server = load_server("the-mcp-server")
# Done.
```

**One line. Everything works.**

---

## Installation

```bash
pip install functional-mcp
```

---

## Type Generation

Generate typed interfaces from server schemas:

```python
from functional_mcp import load_server

server = load_server("weather-server")

# Generate Pydantic models
server.tools.generateTypes(
    path='./types/weather.py',
    format='pydantic',        # or 'dataclass', 'typescript'
    only='input',             # or 'output', None for both
    with_instructions=True    # Include docstrings
)

# Creates:
# class GetForecastInput(BaseModel):
#     '''Get weather forecast for a location.'''
#     lat: float = Field(description='Latitude')
#     lon: float = Field(description='Longitude')
#     units: str = Field(default='metric')

# Now use with full type safety
from types.weather import GetForecastInput

forecast_input = GetForecastInput(lat=25.76, lon=-80.19)
result = server.get_forecast(**forecast_input.model_dump())
```

**Formats:** Pydantic (validation), dataclass (lightweight), TypeScript (frontend)

**When to use:** Type-safe workflows, team collaboration, frontend integration

---

## Framework-Agnostic

Works with **anything**:

```python
from functional_mcp import load_server

# Use with AI agents
from remodl.agents import create_agent
tools = load_server("tools-server")
agent = create_agent(tools=tools.tools)

# Use with DSPy
import dspy
tools = load_server("tools-server")
react = dspy.ReAct(Signature, tools=tools.tools)

# Use with LangChain
from langchain import create_tool
tools = load_server("tools-server")
chain = prompt | model | tools.tools

# Use with Claude/OpenAI directly
from anthropic import Anthropic
tools = load_server("tools-server")
client.messages.create(tools=tools.tools, ...)

# Use standalone
tools = load_server("tools-server")
result = tools.do_thing(params="...")
```

**The MCP server doesn't care. Your code doesn't care. It just works.**

---

## What You Can Load

**Anything with an MCP interface:**

### Local Services
```python
# Your Python scripts
custom = load_server("python my_service.py")

# Node.js services
node = load_server("npx my-node-service")

# Any subprocess
service = load_server("./my-binary --serve")
```

### Remote Services
```python
# HTTP servers
api = load_server("https://api.example.com/mcp")

# With authentication
secure = load_server("https://api.example.com/mcp",
             headers={"Authorization": "Bearer ..."})

# OAuth (browser opens automatically)
oauth_api = load_server("https://api.example.com/mcp", auth="oauth")
```

### Examples
- Filesystem operations
- Database queries
- Email/Calendar/Slack
- GitHub/GitLab operations
- Search engines
- Data pipelines
- Custom business logic
- Literally anything

**If it speaks MCP, it's one `load_server()` away.**

---

## Tool Customization

Generic MCP tools → Agent-specific functions:

```python
from functional_mcp import load_server, transform_tool, ArgTransform

# Generic email server
email = load_server("email-server")

# Make it specific (hide complexity)
send_to_team = transform_tool(
    email.send_message,
    name="notify_team",
    transform_args={
        "to": ArgTransform(hide=True, default="team@company.com"),
        "from": ArgTransform(hide=True, default="noreply@company.com"),
        # Only expose what matters
        "subject": ArgTransform(description="Email subject"),
        "body": ArgTransform(description="Email content"),
    }
)

# Now simpler
send_to_team(subject="Deploy Done", body="All systems operational")
```

**Hide parameters. Set defaults. Rename for clarity. Make tools agent-ready.**

---

## Automatic Intelligence

### Types & Documentation

```python
server = load_server("any-mcp-server")

# Your IDE immediately knows:
server.process_data(
    input="...",    # ← Type hint: str
    format="...",   # ← Type hint: str  
    validate=True   # ← Type hint: bool
)  # ← Return type: dict[str, Any]
```

**Full autocomplete. Instant documentation. Zero configuration.**

### Authentication

```python
# OAuth? Browser opens. You log in. Done.
server = load_server("https://secure-api.com/mcp", auth="oauth")

# Token? Reads from environment automatically.
# Or pass it:
server = load_server("https://api.com/mcp", headers={"Auth": "..."})
```

### Error Handling

```python
from functional_mcp import MCPToolError, MCPConnectionError

try:
    result = server.risky_operation(data="...")
except MCPToolError as e:
    print(f"Tool {e.tool_name} failed: {e}")
except MCPConnectionError:
    print("Server unavailable")
```

**Pythonic exceptions. Clear error messages.**

---

## Server Registry

Connect once. Use everywhere:

```python
from functional_mcp import register, load

# In your setup script (run once):
register(
    email="npx email-mcp-server",
    database="python db_server.py",
    api="https://api.company.com/mcp"
)

# In your code (use anywhere):
email = load_server("email")
db = load_server("database")  
api = load_server("api")
```

**No hardcoded commands. No environment variables. Just names.**

---

## Async Support

```python
from functional_mcp import aload

# Everything becomes async
server = await aload_server("service")

# Concurrent operations
results = await asyncio.gather(
    server.task_1(),
    server.task_2(),
    server.task_3(),
)
```

---

## Real Power: Composition

```python
from functional_mcp import load_server

# Load multiple services
email = load_server("email")
calendar = load_server("calendar")
github = load_server("github")
slack = load_server("slack")

# Compose them into workflows
def handle_pr_merged(pr_number):
    # Get PR
    pr = github.get_pr(number=pr_number)
    
    # Schedule celebration
    calendar.create_event(
        title=f"🎉 PR #{pr_number} shipped!",
        attendees=pr["reviewers"]
    )
    
    # Notify team
    slack.send(
        channel="engineering",
        text=f"PR #{pr_number} by {pr['author']} is live!"
    )
    
    # Send thank you
    email.send(
        to=pr["author"],
        subject="Nice work!",
        body="Your PR shipped successfully."
    )

# One function. Four services. Zero integration code.
handle_pr_merged(1234)
```

**MCP is the standard. functional-mcp is the translator.**

---

## For AI Developers

```python
from functional_mcp import load_server
from remodl.agents import create_agent

# Load real capabilities
tools = load_server("company-tools-server")

# Agent gets real powers
agent = create_agent(
    name="Infrastructure Agent",
    role="Deploy code, manage resources, handle incidents",
    tools=tools.tools
)

# Agent can actually execute
agent.execute("""
Deploy the latest build to staging,
run the test suite,
and notify the team when it's ready.
""")
```

**Not simulated actions. Real infrastructure control.**

**This is the difference between agents that talk and agents that do.**

---

## Philosophy

**MCP servers are the future of service integration.**

They describe tools, resources, and prompts in a standard way.

**functional-mcp makes that future instant.**

No SDK per service. No integration per tool. No learning per API.

**Just Python.**

---

## Status

functional-mcp is production-ready:
- ✅ Complete MCP protocol support
- ✅ Full type safety and IDE integration
- ✅ Robust error handling
- ✅ Authentication (OAuth, Bearer, Custom)
- ✅ Tool customization
- ✅ Framework-agnostic
- ✅ Async support

---

<p align="center">
    <strong>MCP → Python. Automatically. Universally.</strong>
</p>

<p align="center">
    Made with ❤️ by <a href="https://remodl.ai">RemodlAI</a>
</p>
