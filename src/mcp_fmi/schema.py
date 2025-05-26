from typing import List, Dict
from pydantic import BaseModel, HttpUrl

class DataModel(BaseModel):
    timestamps: List[float]
    signals:    Dict[str, List[float]] 

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