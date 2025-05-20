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
from src.fmu_utils import get_fmu_paths, get_fmu_info, FMUCollection

load_dotenv()

BASE_DIR   = Path(__file__).parent
FMU_DIR    = (BASE_DIR / "static" / "fmus").resolve()

#### pydantic classes ####
class FMUList(BaseModel):
    """Absolute paths to all .fmu models that can be simulated."""
    fmu_paths: List[str]
    
class FMUOutputs(BaseModel):
    timestamps: List[float]
    outputs:    Dict[str, List[float]]

class FMIInfo(BaseModel):
    name: str
    relative_path: str
    inputs: Dict[str, str]
    outputs: Dict[str, str]

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
def get_informaiton_of_all_fmus() -> FMUCollection:
    """Lists all FMU models with full metadata, variables, and simulation defaults."""
    fmu_paths_list = get_fmu_paths(FMU_DIR)          # returns FMUPaths
    infos: Dict[str,str] = {}

    for pth in fmu_paths_list.fmu_paths:
        full_path = FMU_DIR / Path(pth).name
        info = get_fmu_info(str(full_path))
        infos[info.name] = info

    return FMUCollection(fmus=infos)

@mcp.tool()
def simulate(fmu_name: str) -> FMUOutputs:
    """This tool simulates an FMU model.
    
    Args:
    fmu_name (str): The name of the FMU model to be simulated. 
    """
    # simulate
    fmu_path = FMU_DIR / f"{fmu_name}.fmu"
    if not fmu_path.is_file():
        raise FileNotFoundError(f"FMU not found: {fmu_path}")
    
    #simulate fmu
    result = simulate_fmu(str(fmu_path))

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
