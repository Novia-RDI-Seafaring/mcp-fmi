# mcp-fmu

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
```cmd
mcp dev server.py
```
or 
```cmd
uv run mcp dev server.py
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