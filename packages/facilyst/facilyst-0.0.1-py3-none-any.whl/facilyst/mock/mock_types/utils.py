import numpy as np
import pandas as pd


def handle_data_and_library_type(data_type="features", library="pandas"):
    if data_type.lower() in ["df", "dataframe", "features", "x"]:
        data_type_ = "features"
    elif data_type.lower() in ["series", "target", "label", "y"]:
        data_type_ = "target"
    else:
        data_type_ = "features"

    if library.lower() in ["pd", "pandas", "df", "dataframe", "series"]:
        library_ = "pandas"
    elif library.lower() in ["np", "numpy", "array", "ndarray"]:
        library_ = "numpy"
    else:
        library_ = "pandas"

    return data_type_, library_


def mock_dtypes(num_rows=100):
    """
    Internal function that returns the default full dataset.

    :param num_rows: The number of observations in the final dataset. Defaults to 100.
    :return: The dataset with all columns included.
    """
    dtypes_dict = {
        "ints": [i for i in range(-num_rows // 2, num_rows // 2)],
        "rand_ints": np.random.choice([i for i in range(-5, 5)], num_rows),
        "floats": [float(i) for i in range(-num_rows // 2, num_rows // 2)],
        "rand_floats": np.random.uniform(low=-5.0, high=5.0, size=num_rows),
        "booleans": np.random.choice([True, False], num_rows),
        "categoricals": np.random.choice(
            ["First", "Second", "Third", "Fourth"], num_rows
        ),
        "dates": pd.date_range("1/1/2001", periods=num_rows),
        "texts": [
            f"My children are miserable failures, all {i} of them"
            for i in range(num_rows)
        ],
        "ints_with_na": np.random.choice(
            [i for i in range(-10 // 2, 10 // 2)] + [pd.NA], num_rows
        ),
        "floats_with_na": np.random.choice(
            np.append([float(i) for i in range(-5, 5)], pd.NA), num_rows
        ),
    }
    return dtypes_dict
