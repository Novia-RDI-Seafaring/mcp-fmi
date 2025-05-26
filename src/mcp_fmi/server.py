# server.py
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from typing import List
from pathlib import Path
from mcp.server.fastmcp import FastMCP

from mcp_fmi.inputs import create_signal, merge_signals
from mcp_fmi.simulation import fmu_information, simulate, simulate_with_input
from mcp_fmi.schema import FMUCollection, DataModel
from mcp_fmi.artifacts import plot_in_browser

from dash import dcc, html

load_dotenv()

FMU_DIR = os.getenv("FMU_DIR", (Path(__file__).parents[2] / "static" / "fmus").resolve())

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

#### tools ####

@mcp.tool()
def fmu_information_tool() -> FMUCollection:
    return fmu_information(FMU_DIR)

@mcp.tool()
def simulate_tool(
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
    return simulate(FMU_DIR, fmu_name, start_time, stop_time, output_interval, tolerance)

@mcp.tool()
def simulate_with_input_tool(
    inputs: DataModel,
    fmu_name: str = "LOC",
    start_time: float = 0.0,
    stop_time: float = 300.0,
    output_interval: float = 5,
    tolerance: float = 1E-4,
    ) -> DataModel:
    """This tool simulates an FMU model with inputs.
    """
    return simulate_with_input(FMU_DIR, fmu_name, start_time, stop_time, output_interval, tolerance, inputs)

@mcp.tool()
def create_signal_tool(
    signal_name: str,
    timestamps: List[float],
    values: List[float]
) -> DataModel:
    """Creates a single signal.
    Args:
    signal_name (str): Name of the signal
    timestamps (List(float)): List of timestamps
    values (List(float)): List of signal values corresponsing to the tiemstamps.

    Returns:
    DataModel
    """
    return create_signal(signal_name,timestamps,values)

@mcp.tool()
def merge_signals_tool(signals: List[DataModel]) -> DataModel:
    """Merges multiple signals into signle DataModel.
    Args:
    signals List[DataModel]: List of signals

    Returns:
    DataModel
    """
    return merge_signals(signals)

@mcp.tool()
def show_results_in_browser_tool(
    inputs: DataModel,
    outputs: DataModel
):
    """Visualizes the results in browser.
    Args:
    inputs (DataModel): input signals used in the simulation
    outputs (DataModel): outputs from a simulation

    Returns:
    HttpURL to the visualizations 
    """
    return plot_in_browser(inputs, outputs)


def main():
    mcp.run()

if __name__ == "__main__":
    main()
