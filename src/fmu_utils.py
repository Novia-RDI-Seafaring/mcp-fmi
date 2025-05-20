import os
from pydantic import BaseModel
from typing import List, Dict
from pathlib import Path
from fmpy import simulate_fmu, plot_result, read_model_description

class FMUPaths(BaseModel):
    fmu_paths: List[str]

class FMUVariables(BaseModel):
    inputs: Dict[str, str]
    outputs: Dict[str, str]
    parameters: Dict[str, str]

class FMUMetadata(BaseModel):
    fmi_version: str
    model_name: str
    author: str
    version: str
    license: str
    generation_tool: str
    generation_date_and_time: str

class FMUSimulation(BaseModel):
    start_time: float
    stop_time: float
    tolerance: float

class FMUInfo(BaseModel):
    name: str
    relative_path: str
    description: str
    variables: FMUVariables
    metadata: FMUMetadata
    simulation: FMUSimulation

class FMUCollection(BaseModel):
    """Returns a collection of all available FMU models and their information."""
    fmus: Dict[str, FMUInfo]

pth = "fmus/BouncingBall.fmu"

def get_additional_information(path: Path) -> str:
    """Gets additional information of an FMU model at fmu_path."""
    md_path = path.with_suffix('.md')
    return md_path.read_text("utf-8") if md_path.is_file() else ""

def get_fmu_info(fmu_path: str) -> FMUInfo:
    """
    Reads the FMU at fmu_path and returns an FMUInfo object
    containing variables, metadata, and simulation settings.
    """
    path = Path(fmu_path)
    md = read_model_description(str(path))

    # Gather variables by causality
    inputs = {v.name: v.type for v in md.modelVariables if v.causality == 'input'}
    outputs = {v.name: v.type for v in md.modelVariables if v.causality == 'output'}
    parameters = {v.name: v.type for v in md.modelVariables if v.causality == 'parameter'}

    variables = FMUVariables(
        inputs=inputs,
        outputs=outputs,
        parameters=parameters
    )

    # Metadata with safe fallbacks
    metadata = FMUMetadata(
        fmi_version=md.fmiVersion or '',
        author=md.author or '',
        version=md.version or '',
        license=md.license or '',
        generation_tool=md.generationTool or '',
        generation_date_and_time=md.generationDateAndTime or ''
    )

    # Simulation defaults with safe fallback for None
    default_exp = md.defaultExperiment
    simulation = FMUSimulation(
        start_time=default_exp.startTime if default_exp.startTime is not None else 0.0,
        stop_time=default_exp.stopTime if default_exp.stopTime is not None else 0.0,
        tolerance=default_exp.tolerance if default_exp.tolerance is not None else 0.0
    )

    base_description = md.description or '' # get base description from FMU model
    additional_description = get_additional_information(path) # get additional information from markdown
    full_description = f"{base_description}\n\n{additional_description}" if additional_description else base_description

    return FMUInfo(
        name=md.modelName or '',
        relative_path=str(path),
        description=full_description,
        variables=variables,
        metadata=metadata,
        simulation=simulation
    )

def get_fmu_paths() -> FMUPaths:
    """Lists the paths all available FMU models that can be simulated."""
    fmu_dir = Path(os.getenv("FMU_DIR", "fmus"))
    if not fmu_dir.is_dir():
        return FMUPaths(fmu_paths=[])

    paths = [
        f.as_posix()
        for f in fmu_dir.glob("*.fmu")
        if f.is_file()
    ]
    return FMUPaths(fmu_paths=paths)