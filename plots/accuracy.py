import xml.etree.ElementTree as ET
from ast import literal_eval

import pandas as pd
import plotly.graph_objects as go

from plots.base import FigureFactoryBase

# from pandera import Column, DataFrameSchema, Int, String, Check


class AccuracyFigureFactory(FigureFactoryBase):
    def __init__(self):
        self.schema = None  # TODO
        self.layout = go.Layout(
            title="Sleep Accuracy",
            yaxis={"title": {"text": "Diff. Actual and Target Sleep Duration (s)"}},
            xaxis={"title": {"text": "Target Sleep Duration (s)"}},
        )

    def parse_dataset(self, data):
        """Parse the file

        @return dataframe with required info for creating trace
        """
        root = ET.fromstring(data)

        accuracy_rows = []
        backoff = literal_eval(
            root.find(
                "testcase[@classname='tests_timer_benchmarks.Sleep Accuracy']//property[@name='xtimer-backoff']"
            ).get("value")
        )
        for prop in root.findall(
            "testcase[@classname='tests_timer_benchmarks.Sleep Accuracy']//property"
        ):
            name = prop.get("name")
            if "accuracy" in name:
                function = name.split("-")[-2]
                target = literal_eval(name.split("-")[-1]) / 1_000_000  # convert to sec
                actuals = literal_eval(prop.get("value"))

                for i, v in enumerate(actuals):
                    accuracy_rows.append(
                        {
                            "target_duration": target,
                            "actual_duration": v,
                            "diff_actual_target": v - target,
                            "repeat": i,
                            "backoff": backoff,
                            "type": function,
                        }
                    )

        return pd.DataFrame(accuracy_rows)

    def make_trace(self, id, data):
        """Make trace for given dataset labeled with id"""
        # self.schema.validate(df)   # TODO

        traces = []
        accuracy = self.parse_dataset(data)
        for typ, backoff in accuracy.groupby(["type", "backoff"]).groups.keys():
            df = accuracy.query(f"type == '{typ}' and backoff == {backoff}")
            traces.append(
                go.Scatter(
                    x=df["target_duration"],
                    y=df["diff_actual_target"],
                    name=f"{typ} / {backoff}",
                ).to_plotly_json()
            )
        return traces

    def make_figure(self, traces):
        if not isinstance(traces, list):
            raise RuntimeError('"traces" must be a list of traces from make_trace')

        return go.Figure(
            {
                "data": traces,
                "layout": self.layout,
            }
        )
