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

def step_input(
    fmu_path: Path,
    start_time: float,
    stop_time: float,
    dt: float,
    step_input_name: List[str],
    step_time: List[float],
    start_value: List[float],
    stop_value: List[float]
) -> DataModel:
    """Build step inputs for a list of FMU inputs"""
    md = read_model_description(str(fmu_path))
    input_vars = [v.name for v in md.modelVariables if v.causality == "input"]

    # validate lengths
    N = len(step_input_name)
    if not (len(step_time)==len(start_value)==len(stop_value)==N):
        raise ValueError("step_time, start_value, stop_value must match length of step_input_name")
    for name in step_input_name:
        if name not in input_vars:
            raise ValueError(f"Unknown input '{name}', valid inputs: {input_vars}")

    time = np.arange(start_time, stop_time + dt, dt)
    signals: Dict[str, List[float]] = {}

    for var in input_vars:
        if var in step_input_name:
            idx = step_input_name.index(var)
            t0 = start_time + step_time[idx]
            sv = start_value[idx]
            ev = stop_value[idx]
            signals[var] = np.where(time < t0, sv, ev).tolist()
        else:
            signals[var] = np.zeros_like(time).tolist()

    return DataModel(timestamps=time.tolist(), signals=signals)

def convert_data(inputs: DataModel, input_vars: List[str]) -> np.ndarray:
    """Turn DataModel (inputs only) into structured array for FMPy"""
    time = np.array(inputs.timestamps)
    dtype = [('time','f8')] + [(name,'f8') for name in input_vars]
    rows = []
    for i in range(len(time)):
        row = (time[i],) + tuple(inputs.signals[name][i] for name in input_vars)
        rows.append(row)
    return np.array(rows, dtype=dtype)

def simulate_fmu_with_inputs(
    fmu_path: Path,
    start_time: float,
    stop_time: float,
    output_interval: float,
    tolerance: float,
    inputs: DataModel
) -> DataModel:
    """Simulate FMU using those inputs, return a DataModel with ALL signals"""
    md = read_model_description(str(fmu_path))
    input_vars  = [v.name for v in md.modelVariables if v.causality == "input"]
    output_vars = [v.name for v in md.modelVariables if v.causality == "output"]

    results = simulate_fmu(
        filename           = str(fmu_path),
        start_time         = start_time,
        stop_time          = stop_time,
        output_interval    = output_interval,
        relative_tolerance = tolerance,
        input              = convert_data(inputs, input_vars),
        output             = output_vars
    )

    timestamps = results['time'].tolist()
    outputs: Dict[str, List[float]] = {
        name: results[name].tolist()
        for name in results.dtype.names if name != 'time'
    }

    return DataModel(timestamps=timestamps, signals=outputs)

def make_figure(
    signals: DataModel,
    title: str
) -> go.Figure:
    """Standalone function to create a figure for given variables"""
    fig = make_subplots(
        rows=len(signals.signals) if signals.signals else 1,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05
    )

    if signals.signals:
        for i, var in enumerate(signals.signals, start=1):
            fig.add_trace(
                go.Scatter(
                    x=signals.timestamps,
                    y=signals.signals[var],
                    name=var,
                    mode='lines'
                ),
                row=i, col=1
            )
    fig.update_layout(
        height=300 * (len(signals.signals) or 1),
        title_text=title,
        xaxis_title="Time (s)",
        yaxis_title="Value",
        template="plotly_white"
    )
    return fig

def build_dash_layout(
    inputs: DataModel,
    outputs: DataModel
) -> html.Div:
    """Build a Dash layout from a DataModel"""
    return html.Div([
        dcc.Tabs([
            dcc.Tab(label="Inputs", children=[
                dcc.Graph(figure=make_figure(inputs, "Inputs"))
            ]),
            dcc.Tab(label="Outputs", children=[
                dcc.Graph(figure=make_figure(outputs, "Outputs"))
            ])
        ])
    ])

def plot_in_browser(inputs: DataModel, outputs: DataModel):
    """Helper to spin up Dash in your browser"""
    app = dash.Dash(__name__)
    app.layout = build_dash_layout(inputs, outputs)
    app.run(debug=True, port=8051)

################################
if __name__ == "__main__":
    fmu_path = Path("static/fmus/LOC.fmu")

    # generate step inputs
    inputs = step_input(
        fmu_path           = fmu_path,
        step_input_name    = [
            "INPUT_temperature_cold_circuit_inlet",
            "INPUT_massflow_cold_circuit",
            "SETPOINT_temperature_lube_oil",
            "INPUT_engine_load_0_1"
        ],
        start_time         = 0.0,
        dt                  = 1.0,
        stop_time          = 10*60.0,
        step_time          = [0.0, 0.0, 5*60, 0.0],
        start_value        = [50.0, 10.0, 80.0, 1.0],
        stop_value         = [50.0, 10.0, 80.0, 1.0]
    )

    # simulate FMU
    outputs = simulate_fmu_with_inputs(
        fmu_path        = fmu_path,
        start_time      = 0.0,
        stop_time       = 10*60.0,
        output_interval = 1.0,
        tolerance       = 1e-4,
        inputs          = inputs
    )

    # launch the interactive UI
    plot_in_browser(inputs=inputs, outputs=outputs)
