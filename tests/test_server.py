import pytest
from mcp_fmi.server import mcp, ping  # make sure you're importing the right mcp instance

@pytest.mark.asyncio
async def test_ping_tool():
    result = await mcp.call_tool("ping", {})
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].text == "pong"
