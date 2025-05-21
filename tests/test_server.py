from mcp.server.fastmcp import FastMCP
import pytest

mcp = FastMCP("mcp-fmu")

@pytest.mark.asyncio
async def test_ping_tool():
    # Call the ping tool
    result = await mcp.call_tool("ping", {})
    assert result == "pong"
