import numpy as np
import pandas as pd
import pytest

from facilyst.mocks import Target


def test_target_default():
    target_class = Target()
    assert target_class.name == "Target"

    target = target_class.get_data()
    assert target.name == "ints"
    assert target.shape == (100,)
    assert target_class.library == "pandas"
    assert list(target_class.parameters.keys()) == ["target_dtype"]


@pytest.mark.parametrize("library", ["PANDAS", "Numpy", "third_option"])
@pytest.mark.parametrize("num_rows", [10, 100, 300, 1000, 10000])
@pytest.mark.parametrize(
    "target_dtype",
    [
        "",
        "ints",
        "rand_ints",
        "floats",
        "rand_floats",
        "booleans",
        "categoricals",
        "dates",
        "texts",
        "ints_with_na",
        "floats_with_na",
    ],
)
def test_target_parameters(library, num_rows, target_dtype):
    kw_args = locals()
    target_class = Target(**kw_args)
    target = target_class.get_data()

    if library.lower() in ["pandas", "third_option"]:
        assert isinstance(target, pd.Series)
        assert target.name == target_dtype if target_dtype else "ints"
    else:
        assert isinstance(target, np.ndarray)

    assert target.shape == (num_rows,)
