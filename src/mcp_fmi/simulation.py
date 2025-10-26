import os
from pydantic import BaseModel, Field
from typing import List, Dict, Union, Callable, Sequence, Any, Optional
from pathlib import Path
from fmpy import simulate_fmu, read_model_description
from fmpy.model_description import ModelDescription
import numpy as np

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

def _simulate_fmu(
    FMU_DIR: Path,
    fmu_name: str,
    start_time: float = 0.0,
    stop_time: float = 1.0,
    solver: str = 'CVode',
    step_size: Optional[float] = None,
    relative_tolerance: Optional[float] = None,
    output_interval: Optional[float] = None,
    record_events: bool = True,
    fmi_type: Optional[str] = None,
    start_values: Dict[str, float] = None,
    input: Optional[Union[DataModel, None]] = None,
    output: Optional[List[str]] = None,
    timeout: Optional[float] = None,
    debug_logging: bool = False,
    visible: bool = False,
    set_input_derivatives: bool = False,
    remote_platform: str = 'auto',
    early_return_allowed: bool = False,
    use_event_mode: bool = False,
    initialize: bool = True,
    terminate: bool = True,
) -> DataModel:
    """Simulate FMU using FMPy and return results as DataModel.
    
    This is a simplified wrapper around FMPy's simulate_fmu that:
    - Handles FMU path construction
    - Converts DataModel input to numpy array for FMPy
    - Converts FMPy results back to DataModel
    - Provides sensible defaults for most parameters
    """
    
    if start_values is None:
        start_values = {}
    
    fmu_path = FMU_DIR / f"{fmu_name}.fmu"
    if not fmu_path.is_file():
        raise FileNotFoundError(f"FMU not found: {fmu_path}")

    # Convert DataModel input to numpy array if provided and not empty
    input_array = None
    if input is not None and hasattr(input, 'timestamps') and input.timestamps:
        input_array = data_model_to_ndarray(input)

    # Call FMPy's simulate_fmu with all parameters
    results = simulate_fmu(
        filename=str(fmu_path),
        validate=True,
        start_time=start_time,
        stop_time=stop_time,
        solver=solver,
        step_size=step_size,
        relative_tolerance=relative_tolerance,
        output_interval=output_interval,
        record_events=record_events,
        fmi_type=fmi_type,
        start_values=start_values,
        apply_default_start_values=False,
        input=input_array,
        output=output,
        timeout=timeout,
        debug_logging=debug_logging,
        visible=visible,
        logger=None,
        fmi_call_logger=None,
        step_finished=None,
        model_description=None,
        fmu_instance=None,
        set_input_derivatives=set_input_derivatives,
        remote_platform=remote_platform,
        early_return_allowed=early_return_allowed,
        use_event_mode=use_event_mode,
        initialize=initialize,
        terminate=terminate,
        fmu_state=None,
        set_stop_time=True
    )

    return ndarray_to_data_model(results)
