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

from mcp_fmu.simulation import simulate_fmus, get_all_fmu_information
from mcp_fmu.schema import FMUCollection, DataModel

load_dotenv()

BASE_DIR   = Path(__file__).parents[2]
FMU_DIR    = (BASE_DIR / "static" / "fmus").resolve()

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

@mcp.tool()
def fmu_information() -> FMUCollection:
    return get_all_fmu_information(FMU_DIR)

@mcp.tool()
def fmu_simulation(
    fmu_name: str = "BouncingBall",
    start_time: float = 0.0,
    stop_time: float = 1.0,
    output_interval: float = 0.1,
    tolerance: float = 1E-4
    ) -> DataModel:
    """This tool simulates an FMU model.
    
    Args:
    fmu_name (str): The name of the FMU model to be simulated. 
    """
    return simulate_fmus(FMU_DIR, fmu_name, start_time, stop_time, output_interval, tolerance)

if __name__ == "__main__":
    mcp.run()
