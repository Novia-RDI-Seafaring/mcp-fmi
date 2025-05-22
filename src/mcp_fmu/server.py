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

from mcp_fmu.inputs import step_input
from mcp_fmu.simulation import get_all_fmu_information, simulate, simulate_with_inputs
from mcp_fmu.schema import FMUCollection, DataModel
from mcp_fmu.artifacts import build_dash_layout

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
    return simulate(FMU_DIR, fmu_name, start_time, stop_time, output_interval, tolerance)

@mcp.tool()
def fmu_simulation_with_inputs(
    inputs: DataModel,
    fmu_name: str = "LOC",
    start_time: float = 0.0,
    stop_time: float = 300.0,
    output_interval: float = 5,
    tolerance: float = 1E-4,
    ) -> DataModel:
    """This tool simulates an FMU model with inputs.
    """
    return simulate_with_inputs(FMU_DIR, fmu_name, start_time, stop_time, output_interval, tolerance, inputs)

@mcp.tool()
def create_step_inputs(
    fmu_name: str = "LOC",
    start_time: float = 0.0,
    stop_time: float = 300.0,
    dt: float = 5,
    input_names: List[str] = ["INPUT_temperature_cold_circuit_inlet", "INPUT_massflow_cold_circuit", "SETPOINT_temperature_lube_oil", "INPUT_engine_load_0_1"],
    step_times: List[float] = [0.0, 0.0, 150, 0.0],
    start_values: List[float] = [50.0, 10.0, 80.0, 1.0],
    stop_values: List[float] = [50.0, 10.0, 80.0, 1.0]
    ) -> DataModel:
    return step_input(FMU_DIR,fmu_name,start_time,stop_time,dt,input_names,step_times,start_values,stop_values)

@mcp.tool()
def results_artifact(
    result,
    input_vars,
    output_vars
    ) -> html.Div:
    return build_dash_layout(result, input_vars, output_vars)


def main():
    mcp.run()

if __name__ == "__main__":
    main()
