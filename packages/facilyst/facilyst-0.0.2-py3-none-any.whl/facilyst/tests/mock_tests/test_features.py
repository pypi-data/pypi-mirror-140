import numpy as np
import pytest

from facilyst.mocks import Features


def test_features_default():
    features_class = Features()
    assert features_class.name == "Features"

    features = features_class.get_data()
    assert np.array_equal(
        features.columns, np.array(["ints", "rand_ints", "floats", "rand_floats"])
    )
    assert features.shape == (100, 4)
    assert features_class.library == "pandas"
    assert list(features_class.parameters.keys()) == [
        "ints",
        "rand_ints",
        "floats",
        "rand_floats",
    ]


@pytest.mark.parametrize("library", ["Pandas", "numpy", "third_option"])
@pytest.mark.parametrize("num_rows", [10, 100, 300, 1000, 10000])
@pytest.mark.parametrize(
    "ints, rand_ints, floats, rand_floats, booleans, categoricals, dates, texts, ints_with_na, floats_with_na",
    [
        [True, True, True, True, True, True, True, True, True, True],
        [False, False, False, False, False, False, False, False, False, False],
        [True, True, True, True, False, False, False, False, False, False],
        [False, False, False, False, True, True, True, True, True, True],
        [False, False, False, False, False, False, False, False, True, True],
        [False, False, False, False, False, False, True, True, False, False],
    ],
)
def test_features_parameters(
    library,
    num_rows,
    ints,
    rand_ints,
    floats,
    rand_floats,
    booleans,
    categoricals,
    dates,
    texts,
    ints_with_na,
    floats_with_na,
):
    kw_args = locals()
    features_class = Features(**kw_args)
    features = features_class.get_data()

    all_features = {
        k: v for k, v in kw_args.items() if k not in ["library", "num_rows"]
    }
    features_included = {k: v for k, v in all_features.items() if v}
    num_columns = len(features_included) if features_included else 10

    if library.lower() in ["pandas", "third_option"]:
        assert np.array_equal(
            features.columns,
            np.array(
                list(
                    features_included.keys()
                    if features_included
                    else all_features.keys()
                )
            ),
        )
    assert features.shape == (num_rows, num_columns)


def test_all_dtypes():
    features_class = Features(all_dtypes=True)
    features = features_class.get_data()

    assert features.shape == (100, 10)
