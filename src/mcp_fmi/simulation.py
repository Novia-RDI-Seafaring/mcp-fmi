import os
from pydantic import BaseModel
from typing import List, Dict
from pathlib import Path
from fmpy import simulate_fmu, read_model_description
import numpy as nd

from mcp_fmi.schema import *
from mcp_fmi.information import _get_model_description
from mcp_fmi.inputs import data_model_to_ndarray, ndarray_to_data_model


def simulate(
    FMU_DIR: Path,
    fmu_name: str,
    start_time: float,
    stop_time: float,
    output_interval: float,
    tolerance: float
) -> DataModel:
    "Simulates an FMU model"

    # simulate
    fmu_path = FMU_DIR / f"{fmu_name}.fmu"
    if not fmu_path.is_file():
        raise FileNotFoundError(f"FMU not found: {fmu_path}")
        
    #simulate fmu
    results = simulate_fmu(
        filename=str(fmu_path),
        start_time=start_time,
        stop_time=stop_time,
        output_interval=output_interval,
        relative_tolerance=tolerance,
        )

    return ndarray_to_data_model(results)

def simulate_with_input(
    FMU_DIR: Path,
    fmu_name: str,
    start_time: float,
    stop_time: float,
    output_interval: float,
    tolerance: float,
    inputs: DataModel
) -> DataModel:
    """Simulate FMU using those inputs, return a DataModel with ALL signals"""

    fmu_path = FMU_DIR / f"{fmu_name}.fmu"
    if not fmu_path.is_file():
        raise FileNotFoundError(f"FMU not found: {fmu_path}")

    results = simulate_fmu(
        filename           = str(fmu_path),
        start_time         = start_time,
        stop_time          = stop_time,
        output_interval    = output_interval,
        relative_tolerance = tolerance,
        input              = data_model_to_ndarray(inputs)
    )

    return ndarray_to_data_model(results)
