from abc import ABC, abstractmethod

import pandas as pd


class Graph(ABC):
    def __init__(self, graph_obj, parameters, extra_parameters):
        self.parameters = parameters
        self.extra_parameters = extra_parameters

        self.check_x_y()
        self.initialize_x_y()

        self.graph_obj = graph_obj(**self.parameters)
        self.resize()
        self.show()

    @property
    @abstractmethod
    def name(self):
        """Name of the graph"""

    def get_figure(self):
        return self.graph_obj.figure.get_figure

    def get_size(self):
        return self.graph_obj.figure.get_size_inches()

    def resize(self, width=11.7, height=8.27):
        self.graph_obj.figure.set_size_inches(width, height)

    def show(self):
        return self.graph_obj.figure

    def check_x_y(self):
        if self.parameters["data"] is None:
            if isinstance(self.parameters["x"], str) or isinstance(
                self.parameters["y"], str
            ):
                raise ValueError(
                    "If dataset is None, then x and y need to contain a collection of data!"
                )
        else:
            if not (
                isinstance(self.parameters["x"], str)
                and isinstance(self.parameters["y"], str)
            ):
                raise ValueError(
                    "If dataset is not None, then x and y need to be strings referring to column names in dataset!"
                )
            if self.parameters["x"] not in self.parameters["data"].columns:
                raise ValueError(
                    f"Column {self.parameters['x']} could not be found in the dataset columns!"
                )
            elif self.parameters["y"] not in self.parameters["data"].columns:
                raise ValueError(
                    f"Column {self.parameters['y']} could not be found in the dataset columns!"
                )

    def initialize_x_y(self):
        if self.parameters["data"] is not None:
            data = self.parameters["data"]
            data.ww.init()
            self.parameters["data"] = data
        else:
            if not isinstance(self.parameters["x"], pd.Series):
                x = pd.Series(self.parameters["x"])
                x.ww.init()
                self.parameters["x"] = x
            if not isinstance(self.parameters["y"], pd.Series):
                y = pd.Series(self.parameters["y"])
                y.ww.init()
                self.parameters["y"] = y
