# server.py
import os
from pickle import NONE
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from typing import List, Optional, Dict, Union, Any, Annotated
from pathlib import Path
import argparse
from mcp.server.fastmcp import FastMCP

from mcp_fmi.inputs import create_signal, merge_signals, data_model_to_ndarray, ndarray_to_data_model
from mcp_fmi.schema import FMUCollection, DataModel, FMUInfo, SimulationModel
from mcp_fmi.information import _get_model_description, _get_all_model_descriptions, _get_fmu_names
from fmpy import simulate_fmu

load_dotenv()

# Default FMU directory path
DEFAULT_FMU_DIR = (Path(__file__).parents[2] / "static" / "fmus").resolve()

def parse_args():
    parser = argparse.ArgumentParser(description='MCP-FMU Server')
    parser.add_argument('fmu_dir', type=str, nargs='?',
                       default=str(DEFAULT_FMU_DIR),
                       help='Path to FMU directory')
    return parser.parse_args()

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
        "mcp-fmu",
        "pydantic",
        "fmpy",
        "python-dotenv",
        "numpy"
    ]
    )

# Get FMU directory from command line args
# Only parse args if not running with MCP dev (which passes the script path as an arg)
if __name__ == "__main__":
    args = parse_args()
    FMU_DIR = Path(args.fmu_dir)
else:
    # When running with MCP dev, use default FMU directory
    FMU_DIR = DEFAULT_FMU_DIR

######### TOOLS #########
GET_ALL_MODEL_DESCRIPTIONS_DESCRIPTION = """
    Lists all FMU models in the directory and their information.
    Returns:
    FMUCollection: Collection of FMU models
"""
@mcp.tool(name="get_model_descriptions", description=GET_ALL_MODEL_DESCRIPTIONS_DESCRIPTION)
def get_all_model_descriptions() -> FMUCollection:
    return _get_all_model_descriptions(FMU_DIR)

GET_MODEL_DESCRIPTION_DESCRIPTION = """
    Gets the model description of a specific FMU model.

    Args:
    fmu_name: Name of the FMU model

    Returns:
    FMUInfo: Full FMU information object
    """
@mcp.tool(name="get_model_description", description=GET_MODEL_DESCRIPTION_DESCRIPTION)
def get_model_description(fmu_name: str) -> FMUInfo:
    return _get_model_description(FMU_DIR, fmu_name)

GET_FMU_NAMES_DESCRIPTION = """Lists the models in the FMU directory.
    Returns:
    List[str]: List of model names
    """
@mcp.tool(name="get_fmu_names", description=GET_FMU_NAMES_DESCRIPTION)
def get_fmu_names() -> List[str]:
    return _get_fmu_names(FMU_DIR)

SIMULATION_DESCRIPTION = """
    Simulates a given FMU model.

    Args:
    sim: SimulationModel containing the simulation parameters
    
    Returns:
    DataModel: Simulation results

    Example JSON call body:
    {
    "fmu_name": "BouncingBall",
    "start_time": 0.0,
    "stop_time": 5.0,
    "output": ["h", "v"],
    "output_interval": 0.1,
    "start_values": {
        "h": 1.0,
        "v": 0.0,
        "g": -9.81
    }
    }
"""
@mcp.tool(name="simulate_fmu", description=SIMULATION_DESCRIPTION)
def simulate_tool(sim: SimulationModel) -> DataModel:

    if sim.start_values is None:
        sim.start_values = {}
    
    fmu_path = FMU_DIR / f"{sim.fmu_name}.fmu"
    if not fmu_path.is_file():
        raise FileNotFoundError(f"FMU not found: {fmu_path}")

    # Convert DataModel input to numpy array if provided and not empty
    input_array = None
    if sim.input is not None and hasattr(sim.input, 'timestamps') and sim.input.timestamps:
        input_array = data_model_to_ndarray(sim.input)

    results = simulate_fmu(
        filename=str(fmu_path),
        start_time=sim.start_time,
        stop_time=sim.stop_time,
        step_size=sim.step_size,
        start_values=sim.start_values,
        input=input_array,
        output=sim.output,
        output_interval=sim.output_interval,
        apply_default_start_values=True,
        record_events=True
    )

    return ndarray_to_data_model(results)

CREATE_SIGNAL_DESCRIPTION =  """Creates a single signal.
    Args:
    signal_name (str): Name of the signal
    timestamps (List(float)): List of timestamps
    values (List(float)): List of signal values corresponsing to the timestamps.

    Returns:
    DataModel
    """
@mcp.tool(name="create_signal", description=CREATE_SIGNAL_DESCRIPTION)
def create_signal_tool(
    signal_name: str,
    timestamps: List[float],
    values: List[float]
) -> DataModel:
    return create_signal(signal_name,timestamps,values)

MERGE_SIGNALS_DESCRIPTION = """Merges multiple signals into single DataModel.
    Args:
    signals List[DataModel]: List of signals

    Returns:
    DataModel
    """
@mcp.tool(name="merge_signals", description=MERGE_SIGNALS_DESCRIPTION)
def merge_signals_tool(signals: List[DataModel]) -> DataModel:

    return merge_signals(signals)

def main():
    mcp.run()

if __name__ == "__main__":
    main()
