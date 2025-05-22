
from pathlib import Path
from typing import List, Dict

from fmpy import read_model_description

import dash
from dash import dcc, html
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from mcp_fmu.schema import DataModel

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



