import pytest
from mcp_fmi.server import mcp, fmu_information_tool  # make sure you're importing the right mcp instance

def test_fmu_information_tool_tool():
    result = fmu_information_tool()
    assert result is not None
