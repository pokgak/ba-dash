from flask import Flask
import requests
import pandas as pd
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go

result_server = "192.168.1.210"
result_server_port = 8080

app = dash.Dash(
    __name__,
    external_stylesheets=["https://unpkg.com/tailwindcss@^1.0/dist/tailwind.min.css"],
)


def get_results():
    r = requests.get(f"http://{result_server}:{result_server_port}/list")
    if r.status_code != 200:
        return [{"version": "NONE", "board": "NONE", "submitter": "NONE"}]
    return r.json()["files"]


def get_metrics():
    files = get_results()
    metrics = set()
    for f in files:
        metrics.update(f["testcases"])
    metrics.discard("Metadata")
    return metrics


def update_metrics_dropdown():
    return dcc.Dropdown(
        options=[{"label": m.capitalize(), "value": m} for m in get_metrics()],
        value="MTL",
        placeholder="Select a metric",
        className="mx-auto",
    )


def update_dataset_table():
    data = get_results()

    INCLUDE_HEADERS = ["board", "version", "submitter"]
    headers = data[0].keys()
    return dash_table.DataTable(
        id="datatable",
        columns=[
            {"name": key.capitalize(), "id": key}
            for key in headers
            if key in INCLUDE_HEADERS
        ],
        data=data,
        filter_action="native",
        row_selectable="multi",
    )


def get_graph():
    return dcc.Graph(id="graph", figure=go.Figure())


app.layout = html.Div(
    [
        html.H1(
            "RIOT Benchmarking Results",
            className="text-bold text-center text-5xl p-10 bg-gray-300",
        ),
        html.Div(
            className="container mx-auto my-10 space-y-10",
            children=[
                html.Div(
                    [html.Div("Step 1: Choose a metric"), update_metrics_dropdown()],
                    className="space-y-3",
                ),
                html.Div(
                    [html.Div("Step 2: Choose dataset(s)"), update_dataset_table()],
                    className="space-y-3",
                ),
            ],
        ),
        html.Div(
            get_graph(), id="graph-container", className="mx-auto lg:w-3/4 md:w-full"
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
