from typing import List, Dict, Optional, Union, Any
from pydantic import BaseModel, HttpUrl, Field

class DataModel(BaseModel):
    timestamps: List[float] = Field(default_factory=list)
    signals:    Dict[str, List[float]] = Field(default_factory=dict)

class FMUPaths(BaseModel):
    fmu_paths: List[str]

class FMUVariables(BaseModel):
    inputs: Dict[str, str]
    outputs: Dict[str, str]
    parameters: Dict[str, str]

class FMUMetadata(BaseModel):
    fmi_version: str
    author: str
    version: str
    license: str
    generation_tool: str
    generation_date_and_time: str

class FMUSimulationOptions(BaseModel):
    start_time: float
    stop_time: float
    tolerance: float

class FMUInfo(BaseModel):
    name: str
    relative_path: str
    description: str
    variables: FMUVariables
    metadata: FMUMetadata
    simulation: FMUSimulationOptions

class FMUCollection(BaseModel):
    """Returns a collection of all available FMU models and their information."""
    fmus: Dict[str, FMUInfo]

class PlotHttpURL(BaseModel):
    description: str
    url: HttpUrl

class SimulationModel(BaseModel):
    fmu_name: str = Field(
        description="Name of the FMU model to simulate"
    )
    start_time: Optional[Union[float, str]] = Field(
        default=0.0,
        description="Simulation start time"
    )
    stop_time: Optional[Union[float, str]] = Field(
        default=1.0,
        description="Simulation stop time"
    )
    step_size: Optional[Union[float, str]] = Field(
        default=None,
        description="Simulation step size"
    )
    input: Optional[DataModel] = Field(
        default=None,
        description="DataModel containing input signals"
    )
    output: Optional[List[str]] = Field(
        default=None,
        description="Sequence of output variable names to record"
    )
    output_interval: Union[float, str] = Field(
        default=None,
        description="Interval for sampling the output"
    )
    start_values: Optional[Dict[str, Any]] = Field(
        default=None,
        description=(
            "Dictionary of initial parameter and input values. "
            "Use this function to change the values of parameters and "
            "inputs from their default values."
        )
    )