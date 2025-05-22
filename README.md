# mcp-fmu

## Prerequisites

- Python 3.13 or higher
- [uv](https://docs.astral.sh/uv/pip/packages/) package manager
- Claude Desktop (for desktop integration)

## Installation

1. Create and activate a virtual environment:
```bash
# Create venv with uv
uv venv

# Activate on macOS/Linux
source .venv/bin/activate

# Activate on Windows
.venv\Scripts\activate
```

2. Install dependencies:
```bash
# Make sure you're in the project root directory
uv pip install -e .
```

## Run the MCP-FMU server
Then add MCP to your project dependencies:
```cmd
uv add "mcp[cli]"
```

To run the mcp command with uv:
```cmd
uv run mcp
```

Test the server with the MCP Inspector:
```bash
uv run --with mcp --with mcp-fmu --with python-dotenv --with fmpy --with numpy --with pydantic mcp dev src/mcp_fmu/server.py
```

## Claude Desktop Integration
Install the MCP server in Claude Desktop by running
```cmd
mcp install server.py
```
it should write the following into the `claude_desktop_config.json` file:
```json
{
  "mcpServers": {
    "MCP-FMU Server": {
      "command": "LOCAL_PATCH_TO_UV\\uv.EXE",
      "args": [
        "run",
        "--with",
        "fmpy",
        "--with",
        "mcp[cli]",
        "--with",
        "pydantic",
        "--with",
        "python-dotenv",
        "mcp",
        "run",
        "LOCAL_PATH_TO_PROJECT\\server.py"
      ]
    }
  }
}
``` 