import seaborn as sns

from . import Graph


class Line(Graph):

    name = "Lineplot"

    def __init__(
        self, x=None, y=None, dataset=None, hue=None, style=None, plot_size=(11.7, 8.27)
    ):
        parameters = {"data": dataset, "x": x, "y": y, "hue": hue, "style": style}

        extra_parameters = {"plot_size": plot_size}

        sns_line = sns.lineplot

        super().__init__(
            graph_obj=sns_line,
            parameters=parameters,
            extra_parameters=extra_parameters,
        )
