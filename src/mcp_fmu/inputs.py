from fmpy import simulate_fmu, read_model_description
from pathlib import Path
from typing import List, Dict
from mcp_fmu.schema import DataModel
import numpy as np

def step_input(
    FMU_DIR: Path,
    fmu_name: str,
    start_time: float,
    stop_time: float,
    dt: float,
    input_names: List[str],
    step_times: List[float],
    start_values: List[float],
    stop_values: List[float]
) -> DataModel:
    """Build step inputs for a list of FMU inputs"""

    fmu_path = FMU_DIR / f"{fmu_name}.fmu"
    md = read_model_description(str(fmu_path))
    input_vars = [v.name for v in md.modelVariables if v.causality == "input"]

    # validate lengths
    N = len(input_names)
    if not (len(step_times)==len(start_values)==len(stop_values)==N):
        raise ValueError("step_time, start_value, stop_value must match length of step_input_name")
    for name in input_names:
        if name not in input_vars:
            raise ValueError(f"Unknown input '{name}', valid inputs: {input_vars}")

    time = np.arange(start_time, stop_time + dt, dt)
    signals: Dict[str, List[float]] = {}

    for var in input_vars:
        if var in input_names:
            idx = input_names.index(var)
            t0 = start_time + step_times[idx]
            sv = start_values[idx]
            ev = stop_values[idx]
            signals[var] = np.where(time < t0, sv, ev).tolist()
        else:
            signals[var] = np.zeros_like(time).tolist()

    return DataModel(timestamps=time.tolist(), signals=signals)

def convert_data(input_model: DataModel, input_vars: List[str]) -> np.ndarray:
    """Convert DataModel (inputs only) into structured array for FMPy"""

    time = np.array(input_model.timestamps)
    dtype = [('time','f8')] + [(name,'f8') for name in input_vars]
    rows = []
    for i in range(len(time)):
        row = (time[i],) + tuple(input_model.signals[name][i] for name in input_vars)
        rows.append(row)
    return np.array(rows, dtype=dtype)

###

def get_input_names(md) -> List[str]:   
    return [v.name for v in md.modelVariables if v.causality == 'input']

def generate_signal(
        input_name: str,
        timestamps: List[float],
        values: List[float]
) -> DataModel:
    """
    Create a DataModel with a single input signal populated with values.
    """
    return DataModel(
        timestamps=timestamps,
        signals={input_name: values}
    )

def merge_signals(signals: List[DataModel]) -> DataModel:
    """
    Merge multiple DataModel instances into a unified model with shared timestamps.
    Assumes piecewise-constant behavior: values hold until the next change.
    """
    #Build global sorted timestamp list
    new_timestamps = sorted(set(t for model in signals for t in model.timestamps))

    # Prepare output signals
    merged_signals = {}

    for s in signals:
        name = list(s.signals.keys())[0]  # only one signal per model
        ts = s.timestamps
        vs = s.signals[name]

        # Map the known values to timestamps
        signal_map = dict(zip(ts, vs))

        # Fill in values across the global timestamp list using last known value
        filled_values = []
        last_value = 0.0  # or None, or a configurable default

        for t in new_timestamps:
            if t in signal_map:
                last_value = signal_map[t]
            filled_values.append(last_value)

        merged_signals[name] = filled_values

    return DataModel(
        timestamps=new_timestamps,
        signals=merged_signals
    )