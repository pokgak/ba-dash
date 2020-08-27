from flask import Flask
import pandas as pd
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go


app = dash.Dash(
    __name__,
    external_stylesheets=["https://unpkg.com/tailwindcss@^1.0/dist/tailwind.min.css"],
)

metrics = ["drift", "jitter", "accuracy"]

data = pd.DataFrame(
    {
        "version": [
            "Release 2020.01",
            "Release 2020.04",
            "Release 2020.07",
            "Release 2020.10",
        ],
        "board": ["samr21-xpro", "yellow", "frdm-kwz2", "bluepill"],
        "submitter": ["abu", "ali", "ahmad", "ci"],
    }
)

# TODO; dynamically load table
data_table = dash_table.DataTable(
    id="datatable",
    columns=[{"name": col.capitalize(), "id": col} for col in data.columns],
    data=data.to_dict(orient="records"),
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
            className="container mx-auto space-y-10",
            children=[
                html.Div(),
                html.Div(
                    [
                        html.Div("Step 1: Choose a metric"),
                        dcc.Dropdown(
                            options=[
                                {"label": m.capitalize(), "value": m} for m in metrics
                            ],
                            value="MTL",
                            placeholder="Select a metric",
                            className="mx-auto",
                        ),
                    ],
                    className="space-y-3",
                ),
                html.Div(
                    [html.Div("Step 2: Choose dataset(s)"), data_table],
                    className="space-y-3",
                ),
            ],
        ),
        html.Div(
            get_graph(), id="graph-container", className="mx-auto lg:w-3/4 md:w-full"
        ),
        html.Footer(
            [
                html.Div("Impressum"),
                html.Div("Contact"),
                html.Div("About"),
            ],
            className="bg-gray-200 flex flex-row justify-center space-x-10 p-5",
        ),
    ],
    className="bg-white",
)

if __name__ == "__main__":
    app.run_server(debug=True)
