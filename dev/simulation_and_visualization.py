from pathlib import Path
from typing import List, Dict
import numpy as np
from pydantic import BaseModel

from fmpy import simulate_fmu, read_model_description

import dash
from dash import dcc, html
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# — 1) Unified DataModel for both inputs and outputs —
class DataModel(BaseModel):
    timestamps: List[float]
    outputs:    Dict[str, List[float]]   # contains every signal: inputs + outputs

# — 2) Build step inputs for a list of FMU inputs —
def step_input(
    fmu_path: Path,
    step_input_name: List[str],
    start_time: float,
    stop_time: float,
    dt: float,
    step_time: List[float],
    start_value: List[float],
    stop_value: List[float]
) -> DataModel:
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

    return DataModel(timestamps=time.tolist(), outputs=signals)

# — 3) Turn DataModel (inputs only) into structured array for FMPy —
def convert_data(input_model: DataModel, input_vars: List[str]) -> np.ndarray:
    time = np.array(input_model.timestamps)
    dtype = [('time','f8')] + [(name,'f8') for name in input_vars]
    rows = []
    for i in range(len(time)):
        row = (time[i],) + tuple(input_model.outputs[name][i] for name in input_vars)
        rows.append(row)
    return np.array(rows, dtype=dtype)

# — 4) Simulate FMU using those inputs, return a DataModel with ALL signals —
def simulate_fmu_with_inputs(
    fmu_path: Path,
    start_time: float,
    stop_time: float,
    output_interval: float,
    tolerance: float,
    input_model: DataModel
) -> DataModel:
    md = read_model_description(str(fmu_path))
    input_vars  = [v.name for v in md.modelVariables if v.causality == "input"]
    output_vars = [v.name for v in md.modelVariables if v.causality == "output"]

    structured_input = convert_data(input_model, input_vars)

    res = simulate_fmu(
        filename           = str(fmu_path),
        start_time         = start_time,
        stop_time          = stop_time,
        output_interval    = output_interval,
        relative_tolerance = tolerance,
        input              = structured_input,
        output             = ['time'] + input_vars + output_vars
    )

    timestamps = res['time'].tolist()
    all_sigs: Dict[str, List[float]] = {
        name: res[name].tolist()
        for name in res.dtype.names if name != 'time'
    }

    return DataModel(timestamps=timestamps, outputs=all_sigs)

# — Standalone function to create a figure for given variables —
def make_figure(
    timestamps: List[float],
    signals: Dict[str, List[float]],
    var_list: List[str],
    title: str
) -> go.Figure:
    vars_present = [v for v in var_list if v in signals]
    fig = make_subplots(
        rows=len(vars_present) if vars_present else 1,
        cols=1,
        shared_xaxes=True,
        subplot_titles=vars_present or [f"No {title.lower()} available."],
        vertical_spacing=0.05
    )
    if vars_present:
        for i, var in enumerate(vars_present, start=1):
            fig.add_trace(
                go.Scatter(
                    x=timestamps,
                    y=signals[var],
                    name=var,
                    mode='lines'
                ),
                row=i, col=1
            )
    fig.update_layout(
        height=300 * (len(vars_present) or 1),
        title_text=title,
        xaxis_title="Time (s)",
        yaxis_title="Value",
        template="plotly_white"
    )
    return fig

# — 5) Build a Dash layout from a DataModel —
def build_dash_layout(
    result: DataModel,
    input_vars: List[str],
    output_vars: List[str]
) -> html.Div:
    return html.Div([
        dcc.Tabs([
            dcc.Tab(label="Inputs", children=[
                dcc.Graph(figure=make_figure(result.timestamps, result.outputs, input_vars, "Inputs"))
            ]),
            dcc.Tab(label="Outputs", children=[
                dcc.Graph(figure=make_figure(result.timestamps, result.outputs, output_vars, "Outputs"))
            ])
        ])
    ])

# — 6) Helper to spin up Dash in your browser —
def plot_in_browser(results: DataModel, fmu_path: Path):
    md = read_model_description(str(fmu_path))
    input_vars  = [v.name for v in md.modelVariables if v.causality == "input"]
    output_vars = [v.name for v in md.modelVariables if v.causality == "output"]

    app = dash.Dash(__name__)
    app.layout = build_dash_layout(results, input_vars, output_vars)
    app.run(debug=True, port=8051)

# — 7) Main: exactly your flow —
if __name__ == "__main__":
    fmu_path = Path("static/fmus/LOC.fmu")

    # generate step inputs
    input_data = step_input(
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
    full_result = simulate_fmu_with_inputs(
        fmu_path        = fmu_path,
        start_time      = 0.0,
        stop_time       = 10*60.0,
        output_interval = 1.0,
        tolerance       = 1e-4,
        input_model     = input_data
    )

    # launch the interactive UI
    plot_in_browser(results=full_result, fmu_path=fmu_path)
