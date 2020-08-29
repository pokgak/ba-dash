import xml.etree.ElementTree as ET
import plotly.graph_objects as go
import pandas as pd
from ast import literal_eval
from pandera import Column, DataFrameSchema, Int, String, Check


class DriftFigureFactory:
    def __init__(self):
        self.schema = DataFrameSchema(
            {
                "killed_by": Column(
                    String,
                ),
                "mut_count": Column(
                    Int,
                    Check(lambda x: x >= 0, element_wise=True, error="mut_count >= 0"),
                ),
            }
        )
        self.layout = go.Layout(
            title="Drift for Sleep Duration seconds",
            yaxis={"title": {"text": "Percentage Actual/Given Sleep Duration [%]"}},
            xaxis={"title": {"text": "X axis do something"}},
            boxmode="group",
        )

    def get_dataset(self, data):
        """Parse the file

        @return dataframe with required info for creating trace
        """
        root = ET.fromstring(data)

        drift_simple_single = dict()
        dss = drift_simple_single
        for testcase in root.findall(
            "testcase[@classname='tests_gpio_overhead.Drift']"
        ):

            for prop in testcase.findall(".//property"):
                # name formatted as 'name'-'unit', we ditch the unit
                name = prop.get("name").split("-")

                repeat_n = int(name[name.index("repeat") + 1])  # repeat count
                # values are recorded as string, convert to float
                value = float(literal_eval(prop.get("value"))[-1])

                key = int(name[2]) / 1_000_000
                if key not in dss:
                    dss[key] = []

                dss[key].append(
                    {
                        "time": key,
                        "repeat": repeat_n,
                        "dut" if "dut" in name else "philip": value,
                    }
                )

        df = pd.DataFrame()
        for k in dss.keys():
            for row in dss[k]:
                df = df.append(row, ignore_index=True)

        # combine dut, philip rows with same (time, repeat) to remove NaN values
        df = df.groupby(["time", "repeat"]).sum()
        df["diff_dut_philip"] = df["dut"] - df["philip"]
        df["diff_percentage"] = df["diff_dut_philip"] / df["dut"] * 100
        df.reset_index(["time", "repeat"], inplace=True)

        return df

    def make_trace(self, id, data):
        """Make trace for given dataset labeled with id"""
        # self.schema.validate(df)   # TODO

        df = self.get_dataset(data)

        return go.Box(x=df["time"], y=df["diff_percentage"], name=id).to_plotly_json()

    def make_figure(self, traces):
        if not isinstance(traces, list):
            raise RuntimeError('"traces" must be a list of traces from make_trace')

        return go.Figure(
            {
                "data": traces,
                "layout": self.layout,
            }
        )
