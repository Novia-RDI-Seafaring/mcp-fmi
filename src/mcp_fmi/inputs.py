from fmpy import simulate_fmu, read_model_description
from pathlib import Path
from typing import List, Dict
from mcp_fmi.schema import DataModel
import numpy as np

def ndarray_to_data_model(data: np.ndarray) -> DataModel:
    """
    Convert a structured numpy array from FMPy into a DataModel.

    Args:
        results: Structured numpy array with a 'time' field and one field per variable.

    Returns:
        DataModel: Contains 'timestamps' and 'signals' for each variable.
    """
    timestamps = data['time'].tolist()
    signals: Dict[str, List[float]] = {
        name: data[name].tolist()
        for name in data.dtype.names
        if name != 'time'
    }
    return DataModel(timestamps=timestamps, signals=signals)

def data_model_to_ndarray(input_model: DataModel) -> np.ndarray:
    """
    Convert a DataModel of inputs into a structured numpy array for FMPy.

    Asgs:
        input_model: DataModel containing 'timestamps' and 'signals'.

    Returns:
        Structured numpy array with dtype [('time', 'f8'), ...] and one row per timestamp.
    """
    # Extract timestamps and variable names
    timestamps = input_model.timestamps
    input_vars = list(input_model.signals.keys())

    # Define structured dtype: time plus each variable in the model
    dtype = [('time', 'f8')] + [(name, 'f8') for name in input_vars]

    # Build each row as a tuple: (time, *values)
    rows = []
    for idx, t in enumerate(timestamps):
        values = tuple(input_model.signals[name][idx] for name in input_vars)
        rows.append((t,) + values)

    return np.array(rows, dtype=dtype)

def create_signal(
        input_name: str,
        timestamps: List[float],
        values: List[float]
) -> DataModel:
    """
    Create a DataModel with a single input signal populated with values.
    Returns:
        Structured numpy array with dtype [('time', 'f8'), ...] and one row per timestamp.
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