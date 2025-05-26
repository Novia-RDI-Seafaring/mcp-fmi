
from pathlib import Path
from typing import List, Dict

from fmpy import read_model_description

import dash
from dash import dcc, html
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from mcp_fmi.schema import DataModel, PlotHttpURL

import threading

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

def plot_in_browser(inputs: DataModel, outputs: DataModel, port: int = 8051) -> PlotHttpURL:
    """Visualizes the results in browser
    Args:
    inputs (DataModel): input signals used in the simulation
    outputs (DataModel): outputs from a simulation

    Returns:
    HttpURL to the visualizations 
    """
    app = dash.Dash(__name__)
    app.layout = build_dash_layout(inputs, outputs)

    def run_app():
        app.run_server(debug=False, port=port, use_reloader=False)

    thread = threading.Thread(target=run_app)
    thread.daemon = True
    thread.start()

    return PlotHttpURL(
        description="URL to visualization of results.",
        url=f"http://localhost:{port}")

