from pathlib import Path
from typing import List, Dict
from fmpy import read_model_description
from mcp_fmi.schema import FMUPaths, FMUVariables, FMUMetadata, FMUSimulationOptions, FMUInfo, FMUCollection

def get_additional_information(path: Path) -> str:
    """Gets additional information of an FMU model at fmu_path."""
    md_path = path.with_suffix('.md')
    return md_path.read_text("utf-8") if md_path.is_file() else ""

def get_default_simulation_options(md):
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
    simulation_description = get_default_simulation_options(md)
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

# tools
def _get_fmu_paths(fmu_dir: Path) -> FMUPaths:
    paths = [f.as_posix() for f in fmu_dir.glob("*.fmu") if f.is_file()]
    return FMUPaths(fmu_paths=paths)

def _get_fmu_names(fmu_dir: Path) -> List[str]:
    """Lists all FMU models in the directory.
    Returns:
    List[str]: List of model names (without .fmu extension)
    """
    return [f.stem for f in fmu_dir.glob("*.fmu") if f.is_file()]

def _get_model_description(FMU_DIR: Path, fmu_name: str) -> FMUInfo:
    """Gets the model description of an FMU model.
    Returns:
    FMUInfo: Full FMU information object
    """
    return get_fmu_information(str(FMU_DIR / f"{fmu_name}.fmu"))

def _get_all_model_descriptions(FMU_DIR: Path) -> FMUCollection:
    """Lists all FMU models with full metadata, variables, and simulation defaults."""
    fmu_paths_list = _get_fmu_paths(FMU_DIR)          # returns FMUPaths
    infos: Dict[str, FMUInfo] = {}

    for pth in fmu_paths_list.fmu_paths:
        full_path = FMU_DIR / Path(pth).name
        info = get_fmu_information(str(full_path))
        infos[info.name] = info

    return FMUCollection(fmus=infos)
