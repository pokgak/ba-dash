from abc import ABC, abstractmethod


class FigureFactoryBase(ABC):
    @abstractmethod
    def parse_dataset(self, data):
        """Parses the dataset and returns a DataFrame

        :param  data: dataset in XML
        :type   data: string

        :return a DataFrame
        """
        pass

    @abstractmethod
    def make_trace(self, id, df):
        """Make a trace

        :param  id: name to use as label for the trace
        :param  df: parsed dataset returned from @ref parse_dataset()

        :return a Plotly trace object e.g. Scatter, Box, etc.
        """
        pass

    @abstractmethod
    def make_figure(self, traces):
        """Make a figure from a list of traces

        :param  traces: traces to use
        :type   traces: list

        :return a Plotly Figure object
        """
        pass