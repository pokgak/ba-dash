import json

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.graph_objects as go
import requests
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from flask import Flask

from plots.accuracy import AccuracyFigureFactory
from plots.drift import DriftFigureFactory

result_server = "127.0.0.1"
result_server_port = 5000

app = dash.Dash(
    __name__,
    external_stylesheets=["https://unpkg.com/tailwindcss@^1.0/dist/tailwind.min.css"],
)


def send_request(path):
    path = path[1:] if path[0] == "/" else path
    return requests.get(f"http://{result_server}:{result_server_port}/{path}")


def get_results():
    r = send_request("/list")
    if r.status_code != 200:
        return [{"version": "NONE", "board": "NONE", "submitter": "NONE"}]
    return r.json()["files"]


def get_metrics():
    files = get_results()
    metrics = set()
    for f in files:
        metrics.update(f["testcases"])
    metrics.discard("metadata")
    return metrics


def create_metrics_dropdown():
    return dcc.Dropdown(
        id="metrics-dropdown",
        options=[{"label": m.capitalize(), "value": m} for m in get_metrics()],
        placeholder="Select a metric",
        className="mx-auto",
    )


@app.callback(
    Output("datasets", "data"),
    Output("datasets", "selected_row_ids"),
    Output("datasets", "selected_rows"),
    Input("metrics-dropdown", "value"),
)
def update_dataset_data(chosen_metric):
    if chosen_metric is None:
        return None, [], []

    data = get_results()
    for d in data:
        d.update({"id": json.dumps(d, sort_keys=True)})
    return (
        [d for d in data if chosen_metric in d["testcases"]],
        [],
        [],  # clear checkbox when new metric is selected
    )


def create_dataset_table():
    data = get_results()

    INCLUDE_HEADERS = ["board", "version", "submitter"]
    headers = data[0].keys()
    return dash_table.DataTable(
        id="datasets",
        columns=[
            {"name": key.capitalize(), "id": key}
            for key in headers
            if key in INCLUDE_HEADERS
        ],
        # data=[],  # let the data updated by the update_dataset_data callback
        filter_action="native",
        row_selectable="multi",
        cell_selectable=False,
        fixed_rows=dict(headers=True, data=5),
    )


def get_figure_factory(metric):
    if metric == "drift":
        return DriftFigureFactory()
    elif metric == "sleep accuracy":
        return AccuracyFigureFactory()
    else:
        raise RuntimeError(f"Unknown metric: {metric}")


@app.callback(
    Output("graph-container", "children"),
    Input("metrics-dropdown", "value"),
    Input("datasets", "selected_row_ids"),
    State("memory", "data"),  # TODO: store id from metrics-dropdown value possible?
)
def update_graph(metric, row_ids, figstore):
    if metric is None:
        return dcc.Graph(id="graph", figure=go.Figure())
    ff = get_figure_factory(metric)

    if row_ids is None:
        return dcc.Graph(id="graph", figure=go.Figure({"layout": ff.layout}))

    if figstore is None:
        figstore = dict()
    if metric not in figstore:
        figstore[metric] = go.Figure()
    fig = figstore[metric]

    traces = []
    for rid in row_ids:
        location = "/results/20200713-dkfqcje.xml"  # FIXME: get location from row id
        r = send_request(location)
        if r.status_code != 200:
            raise RuntimeError(f"Failed to fetch file {location}")
        tmp = ff.make_trace(rid, r.content)
        if isinstance(tmp, dict):
            traces.append(tmp)
        else:
            traces.extend(tmp)

    fig = go.Figure(data=traces, layout=ff.layout)
    return dcc.Graph(id="graph", figure=fig)


app.layout = html.Div(
    [
        dcc.Store(id="memory"),  # TODO: one store per figure type?
        html.H1(
            "RIOT Benchmarking Results",
            className="text-bold text-center text-5xl p-10 bg-gray-300",
        ),
        html.Div(
            className="container mx-auto my-10 space-y-10",
            children=[
                html.Div(
                    [html.Div("Step 1: Choose a metric"), create_metrics_dropdown()],
                    className="space-y-3",
                ),
                html.Div(
                    [html.Div("Step 2: Choose dataset(s)"), create_dataset_table()],
                    className="space-y-3",
                ),
            ],
        ),
        html.Div(
            dcc.Graph(id="graph", figure=go.Figure()),
            id="graph-container",
            className="mx-auto lg:w-3/4 md:w-full",
        ),
        # html.Footer(
        #     [
        #         html.Div("Impressum"),
        #         html.Div("Contact"),
        #         html.Div("About"),
        #     ],
        #     className="bg-gray-200 flex flex-row justify-center space-x-10 p-5",
        # ),
    ],
    className="bg-white",
)

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
