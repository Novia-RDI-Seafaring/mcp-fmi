# server.py
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from typing import List, Dict
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
from fmpy import simulate_fmu, plot_result

load_dotenv()

#### pydantic classes ####
class FMUList(BaseModel):
    fmu_paths: List[str]
    """Absolute paths to all .fmu models that can be simulated."""

class FMUOutputs(BaseModel):
    timestamps: List[float]
    outputs:    Dict[str, List[float]]

##### context manager for loading models on startup ####
@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[None]:
    #on startup
    print("Startup...")
    try:
        yield 
    finally:
        # on shutdown
        print("Shutdown...")

##### Create an MCP server ####
mcp = FastMCP(
    "MCP-FMU Server",
    lifespan=app_lifespan,
    host=os.getenv("HOST") or "0.0.0.0",
    port=os.getenv("PORT") or 8050,
    dependencies=[
        "pydantic",
        "fmpy",
        "python-dotenv"
    ]
    )

#### tools ####
@mcp.tool()
def ping() -> str:
    return "pong"

@mcp.resource("fmus://list")
def get_fmu_paths() -> FMUList:
    """This resource lists all available FMU models that can be simulated."""
    fmu_dir = Path(os.getenv("FMU_DIR", "fmus"))
    if not fmu_dir.is_dir():
        return FMUList(fmu_paths=[])

    paths = [
        f.as_posix()
        for f in fmu_dir.glob("*.fmu")
        if f.is_file()
    ]
    return FMUList(fmu_paths=paths)

@mcp.tool()
def simulate(fmu_path: str) -> FMUOutputs:
    """This tool simulates an FMU model.
    
    Args:
    fmu_path: str
    """
    # simulate
    result = simulate_fmu(fmu_path)

    # get timestamps
    time_key = "time" if "time" in result.dtype.names else "timestamp"
    timestamps = result[time_key].tolist()

    outputs = {
        name: result[name].tolist()
        for name in result.dtype.names
        if name != time_key
    }

    return FMUOutputs(timestamps=timestamps, outputs=outputs)

if __name__ == "__main__":
    mcp.run()
