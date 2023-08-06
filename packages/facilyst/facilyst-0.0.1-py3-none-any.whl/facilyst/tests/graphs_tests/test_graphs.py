import numpy as np
import pandas as pd

from facilyst.graphs import Scatter


def test_default_size_and_resize():
    X = pd.DataFrame()
    X["x_axis"] = [i for i in range(10)]
    X["y_axis"] = [i for i in range(10)]

    scatter = Scatter(x="x_axis", y="y_axis", dataset=X)
    assert np.array_equal(scatter.get_size(), np.array([11.7, 8.27]))

    scatter.resize(20, 10)
    assert np.array_equal(scatter.get_size(), np.array([20, 10]))
