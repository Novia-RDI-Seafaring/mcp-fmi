import os
from pydantic import BaseModel
from typing import List, Dict
from pathlib import Path
from fmpy import simulate_fmu, plot_result, read_model_description

from mcp_fmu.schema import *

def get_fmu_paths(fmu_dir: Path) -> FMUPaths:
    paths = [f.as_posix() for f in fmu_dir.glob("*.fmu") if f.is_file()]
    return FMUPaths(fmu_paths=paths)

def get_additional_information(path: Path) -> str:
    """Gets additional information of an FMU model at fmu_path."""
    md_path = path.with_suffix('.md')
    return md_path.read_text("utf-8") if md_path.is_file() else ""

def get_dafault_simulation_options(md):
    default_exp = md.defaultExperiment
    return FMUSimulationOptions(
        start_time=default_exp.startTime if default_exp.startTime is not None else 0.0,
        stop_time=default_exp.stopTime if default_exp.stopTime is not None else 0.0,
        tolerance=default_exp.tolerance if default_exp.tolerance is not None else 1E-4
    )

def get_fmu_information(fmu_path: str) -> FMUInfo:
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
    simulation_description = get_dafault_simulation_options(md)
    base_description = md.description or '' # get base description from FMU model
    additional_description = get_additional_information(path) # get additional information from markdown
    full_description = f"{base_description}\n\n{additional_description}" if additional_description else base_description

    return FMUInfo(
        name=md.modelName or '',
        relative_path=str(path),
        description=full_description,
        variables=variables,
        metadata=metadata,
        simulation=simulation_description
    )

def get_all_fmu_information(FMU_DIR) -> FMUCollection:
    """Lists all FMU models with full metadata, variables, and simulation defaults."""
    fmu_paths_list = get_fmu_paths(FMU_DIR)          # returns FMUPaths
    infos: Dict[str,str] = {}

    for pth in fmu_paths_list.fmu_paths:
        full_path = FMU_DIR / Path(pth).name
        info = get_fmu_information(str(full_path))
        infos[info.name] = info

    return FMUCollection(fmus=infos)

def simulate_fmus(FMU_DIR: Path,fmu_name: str,start_time: float,stop_time: float,output_interval: float,tolerance: float) -> DataModel:
    
    "Simulates an FMU model"
    # simulate
    fmu_path = FMU_DIR / f"{fmu_name}.fmu"
    if not fmu_path.is_file():
        raise FileNotFoundError(f"FMU not found: {fmu_path}")
        
    #simulate fmu
    result = simulate_fmu(
        filename=str(fmu_path),
        start_time=start_time,
        stop_time=stop_time,
        output_interval=output_interval,
        relative_tolerance=tolerance,
        )

    # get timestamps
    time_key = "time" if "time" in result.dtype.names else "timestamp"
    timestamps = result[time_key].tolist()

    outputs = {
        name: result[name].tolist()
        for name in result.dtype.names
        if name != time_key
    }

    return DataModel(timestamps=timestamps, outputs=outputs)
