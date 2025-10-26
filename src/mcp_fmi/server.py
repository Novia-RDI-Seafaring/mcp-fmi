# server.py
import os
from pickle import NONE
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from typing import List, Optional, Dict, Union, Any, Literal, Sequence
from pydantic import Field
from pathlib import Path
import argparse
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from mcp_fmi.inputs import create_signal, merge_signals, data_model_to_ndarray, ndarray_to_data_model
from mcp_fmi.schema import FMUCollection, DataModel, FMUInfo
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

### Tools retrieving information ###

@mcp.tool()
def get_all_model_descriptions() -> FMUCollection:
    """Gets the information about the FMU models in the directory.
    Returns:
    FMUCollection: Collection of FMU models
    """
    return _get_all_model_descriptions(FMU_DIR)

@mcp.tool()
def get_model_description(fmu_name: str) -> FMUInfo:
    """Gets the model description of an FMU model.
    Returns:
    FMUInfo: Full FMU information object
    """
    return _get_model_description(FMU_DIR, fmu_name)

@mcp.tool()
def get_fmu_names() -> List[str]:
    """Lists the models in the FMU directory.
    Returns:
    List[str]: List of model names
    """
    return _get_fmu_names(FMU_DIR)

### Tool for simulation ###
class Variable(BaseModel):
    name: str = Field(..., description="Name of the variable")
    value: float = Field(..., description="Value of the variable")

class Initialization(BaseModel):
    parameters: Optional[List[Variable]] = Field(
        default=None,
        description="List of parameter values to set"
        )
    initial_inputs: Optional[List[Variable]] = Field(
        default=None,
        description="List of inputs values to set"
        )

class SolverOptions(BaseModel):
    solver: Optional[Literal["Euler", "CVode"]] = Field(
        default="CVode",
        description="Solver to use for model exchange ('Euler' or 'CVode')"
    )
    step_size: Optional[float] = Field(
        default=None,
        description="Step size for the 'Euler' solver"
    )
    relative_tolerance: Optional[float] = Field(
        default=None,
        description="Relative tolerance for the solver"
    )
class ResultsOptions(BaseModel):
    outputs: Sequence[str] = Field(
        default=None,
        description="List of variables to record (empty list: record all outputs)"
        )
    output_interval: Union[float, str] = Field(
        default=None,
        description="Sampling time for sampling the outputs (0.0 means auto)"
        )    

class SimulationOptions(BaseModel):
    solver_options: Optional[SolverOptions] = Field(default=None, description="Solver options")
    results_options: Optional[ResultsOptions] = Field(default=None, description="Results options")

class Experiment(BaseModel):
    fmu_name: str = Field(default="BouncingBall", description="The name of the FMU model to simulate")
    input: Optional[DataModel] = Field(
        default={},
        description="A DataModel containing input signals with timestamps. Omit for models without inputs."
        )
    start_time: Optional[Union[float, str]] = Field(
        default=0.0,
        description="Simulation start time"
        )
    stop_time: Optional[Union[float, str]] = Field(
        default=1.0,
        description="Simulation stop time"
        )
    initialization: Optional[Initialization] = Field(
        default=Initialization(),
        description="Model initialization options"
        )
    options: Optional[SimulationOptions] = Field(
        default=SimulationOptions(),
        description="Simulation options"
        )



@mcp.tool()
def simulate(
    experiment: Experiment = Experiment()
) -> DataModel:
    """Simulate an FMU model with the specified parameters.
    
    This tool simulates an FMU (Functional Mock-up Unit) model using the FMPy library.
    It supports both Model Exchange and Co-Simulation FMUs with various solver options.
    
    Args:
        experiment: Experiment configuration including FMU name, inputs, time range, and initialization
        options: Optional simulation and solver options
        
    Returns:
        DataModel: Simulation results containing all signals
    """
    # Build FMU path
    fmu_path = FMU_DIR / f"{experiment.fmu_name}.fmu"
    if not fmu_path.is_file():
        raise FileNotFoundError(f"FMU not found: {fmu_path}")

    # Convert DataModel input to numpy array if provided and not empty
    input_array = None
    if experiment.input and experiment.input.timestamps:
        input_array = data_model_to_ndarray(experiment.input)

    # Prepare start_values dictionary from initialization
    start_values = {}
    if experiment.initialization:
        # Add parameters
        if experiment.initialization.parameters:
            for param in experiment.initialization.parameters:
                start_values[param.name] = param.value
        # Add initial inputs
        if experiment.initialization.initial_inputs:
            for inp in experiment.initialization.initial_inputs:
                start_values[inp.name] = inp.value

    # Extract solver options with defaults
    solver = 'CVode'
    step_size = None
    relative_tolerance = None
    if experiment.options and experiment.options.solver_options:
        solver = experiment.options.solver_options.solver
        step_size = experiment.options.solver_options.step_size
        relative_tolerance = experiment.options.solver_options.relative_tolerance

    # Extract results options
    output_param = None
    output_interval = None
    if experiment.options and experiment.options.results_options:
        output_param = experiment.options.results_options.outputs
        output_interval = experiment.options.results_options.output_interval

    # Call FMPy's simulate_fmu
    results = simulate_fmu(
        filename=str(fmu_path),
        start_time=experiment.start_time,
        stop_time=experiment.stop_time,
        solver=solver,
        step_size=step_size,
        relative_tolerance=relative_tolerance,
        output_interval=output_interval,
        record_events=True,
        start_values=start_values if start_values else {},
        apply_default_start_values=(not start_values),
        input=input_array,
        output=output_param,
        timeout=None,
        logger=None,
        fmi_call_logger=None,
        step_finished=None,
        model_description=None,
        fmu_instance=None
    )

    # Convert results back to DataModel
    return ndarray_to_data_model(results)

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
    values (List(float)): List of signal values corresponsing to the timestamps.

    Returns:
    DataModel
    """
    return create_signal(signal_name,timestamps,values)

@mcp.tool()
def merge_signals_tool(signals: List[DataModel]) -> DataModel:
    """Merges multiple signals into single DataModel.
    Args:
    signals List[DataModel]: List of signals

    Returns:
    DataModel
    """
    return merge_signals(signals)

def main():
    mcp.run()

if __name__ == "__main__":
    main()
