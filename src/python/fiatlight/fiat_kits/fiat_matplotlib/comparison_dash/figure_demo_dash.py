# type: ignore
import dash
from dash_daq import Knob
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import dash_daq as daq
import numpy as np
import time

app = dash.Dash(__name__)

app.layout = html.Div(
    [
        html.H1("Interactive Plots with Dash"),
        html.Div(id="fps-display", style={"fontSize": "20px", "color": "red"}),
        html.Div(
            [
                html.Label("Frequency"),
                Knob(  # noqa
                    id="freq-slider",
                    min=0.1,
                    max=3,
                    value=1,
                    size=30,
                ),
            ],
            style={"width": "30%", "display": "inline-block"},
        ),
        html.Div(
            [
                html.Label("Amplitude"),
                daq.Knob(
                    id="amplitude-knob",
                    min=0.1,
                    max=2,
                    value=1,
                    size=30,
                ),
            ],
            style={"width": "30%", "display": "inline-block"},
        ),
        dcc.Graph(id="sine-wave", style={"height": "300px"}),
        dcc.Interval(id="interval-component", interval=1000 / 60, n_intervals=0),  # Update at ~60 FPS
        html.Div(
            [
                html.Label("Mean"),
                dcc.Slider(
                    id="mean-slider",
                    min=-5,
                    max=5,
                    step=0.1,
                    value=0,
                    marks={i: f"{i}" for i in range(-5, 6)},
                    updatemode="drag",
                ),
            ],
            style={"width": "30%", "display": "inline-block"},
        ),
        html.Div(
            [
                html.Label("Variance"),
                dcc.Slider(
                    id="variance-slider",
                    min=0.1,
                    max=5,
                    step=0.1,
                    value=1,
                    marks={float(i): f"{i}" for i in np.arange(0.1, 5.1, 1)},
                    updatemode="drag",
                ),
            ],
            style={"width": "30%", "display": "inline-block"},
        ),
        dcc.Graph(id="gaussian-heatmap", style={"height": "300px"}),
        html.Div(
            [
                html.Label("Window Size"),
                dcc.Slider(
                    id="window-size-slider",
                    min=1,
                    max=40,
                    step=1,
                    value=5,
                    marks={i: f"{i}" for i in range(1, 41, 5)},
                    updatemode="drag",
                ),
            ],
            style={"width": "30%", "display": "inline-block"},
        ),
        dcc.Graph(id="data-smoothing", style={"height": "300px"}),
        html.Div(
            [
                html.Label("Number of Bars"),
                dcc.Slider(
                    id="n-bars-slider",
                    min=1,
                    max=300,
                    step=1,
                    value=10,
                    marks={i: f"{i}" for i in range(1, 301, 50)},
                    updatemode="drag",
                ),
            ],
            style={"width": "30%", "display": "inline-block"},
        ),
        html.Div(
            [
                html.Label("Mean"),
                dcc.Slider(
                    id="hist-mean-slider",
                    min=-5,
                    max=5,
                    step=0.1,
                    value=0,
                    marks={i: f"{i}" for i in range(-5, 6)},
                    updatemode="drag",
                ),
            ],
            style={"width": "30%", "display": "inline-block"},
        ),
        html.Div(
            [
                html.Label("Standard Deviation"),
                dcc.Slider(
                    id="sigma-slider",
                    min=0.1,
                    max=5,
                    step=0.1,
                    value=1,
                    marks={float(i): f"{i}" for i in np.arange(0.1, 5.1, 1)},
                    updatemode="drag",
                ),
            ],
            style={"width": "30%", "display": "inline-block"},
        ),
        html.Div(
            [
                html.Label("Average"),
                dcc.Slider(
                    id="average-slider",
                    min=0,
                    max=1000,
                    step=10,
                    value=500,
                    marks={i: f"{i}" for i in range(0, 1001, 200)},
                    updatemode="drag",
                ),
            ],
            style={"width": "30%", "display": "inline-block"},
        ),
        html.Div(
            [
                html.Label("Number of Data Points"),
                dcc.Slider(
                    id="nb-data-slider",
                    min=100,
                    max=10000,
                    step=100,
                    value=1000,
                    marks={int(i): f"{i}" for i in np.logspace(2, 6, num=5, base=10)},
                    updatemode="drag",
                ),
            ],
            style={"width": "30%", "display": "inline-block"},
        ),
        dcc.Graph(id="interactive-histogram", style={"height": "300px"}),
    ]
)

START_TIME = time.time()

last_update_times = []


def average_fps() -> float:
    global last_update_times
    current_time = time.time()
    last_update_times.append(current_time)
    window_length = 20
    if len(last_update_times) >= window_length:
        last_update_times = last_update_times[-window_length:]
        fps = len(last_update_times) / (current_time - last_update_times[0])
        return fps
    else:
        return 0


@app.callback(
    [Output("sine-wave", "figure"), Output("fps-display", "children")],
    [Input("interval-component", "n_intervals"), Input("freq-slider", "value"), Input("amplitude-knob", "value")],
)
def update_sine_wave(n_intervals, freq, amplitude):
    x = np.linspace(0, 2 * np.pi, 3000)
    phase = (time.time() - START_TIME) * 5
    y = amplitude * np.sin(2 * np.pi * freq * x + phase)
    fig = go.Figure(data=go.Scatter(x=x, y=y))
    fig.update_layout(title="Interactive Sine Wave", xaxis_title="x", yaxis_title="y")

    return fig, f"FPS: {average_fps():.2f}"


@app.callback(Output("gaussian-heatmap", "figure"), [Input("mean-slider", "value"), Input("variance-slider", "value")])
def update_gaussian_heatmap(mean, variance):
    x = y = np.linspace(-5, 5, 100)
    X, Y = np.meshgrid(x, y)
    Z = np.exp(-((X - mean) ** 2 + (Y - mean) ** 2) / (2 * variance))
    fig = go.Figure(data=go.Heatmap(z=Z, x=x, y=y))
    fig.update_layout(title="Gaussian Heatmap", xaxis_title="x", yaxis_title="y")
    return fig


@app.callback(Output("data-smoothing", "figure"), [Input("window-size-slider", "value")])
def update_data_smoothing(window_size):
    x = np.linspace(0, 15, 300)
    y = np.sin(x) + np.random.normal(0, 0.1, 300)  # Noisy sine wave
    y_smooth = np.convolve(y, np.ones(window_size) / window_size, mode="same")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name="Original"))
    fig.add_trace(go.Scatter(x=x, y=y_smooth, mode="lines", name="Smoothed"))
    fig.update_layout(title="Data Smoothing", xaxis_title="x", yaxis_title="y")
    return fig


@app.callback(
    Output("interactive-histogram", "figure"),
    [
        Input("n-bars-slider", "value"),
        Input("hist-mean-slider", "value"),
        Input("sigma-slider", "value"),
        Input("average-slider", "value"),
        Input("nb-data-slider", "value"),
    ],
)
def update_histogram(n_bars, mu, sigma, average, nb_data):
    data = np.random.normal(mu, sigma, int(nb_data)) + average
    fig = go.Figure(data=[go.Histogram(x=data, nbinsx=n_bars)])
    fig.update_layout(title="Interactive Histogram", xaxis_title="Value", yaxis_title="Frequency")
    return fig


if __name__ == "__main__":
    app.run_server(debug=False)
