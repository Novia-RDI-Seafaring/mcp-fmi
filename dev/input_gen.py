import os
from pathlib import Path
from typing import List, Dict
import numpy as np
from pydantic import BaseModel

from fmpy import simulate_fmu, read_model_description

import dash
from dash import dcc, html
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from mcp_fmu.schema import DataModel

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

###
input_names = ["input_1", "input_2"]

input1 = generate_signal(
        input_name="input_1",
        timestamps=[0, 2, 4, 8, 10],
        values=[1, 1, 1, 1, 1]
)
input2 = generate_signal(
        input_name="input_2",
        timestamps=[1, 3, 5, 9],
        values=[2, 2, 2, 2]
)
inputs = merge_signals(signals=[input1, input2])

print(inputs.model_dump_json(indent=2))

