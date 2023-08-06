import pytest

from facilyst.mocks.mock_types import handle_data_and_library_type


@pytest.mark.parametrize(
    "data_type",
    ["DataFrame", "features", "series", "Target", "X", "y", "some_features"],
)
@pytest.mark.parametrize("library", ["PANDAS", "Numpy", "pd", "nP", "paddy_cake"])
def test_handle_data_and_library_type(data_type, library):
    data_type_, library_ = handle_data_and_library_type(data_type, library)
    if data_type.lower() in ["dataframe", "features", "x", "some_features"]:
        assert data_type_ == "features"
    else:
        assert data_type_ == "target"
    if library.lower() in ["pandas", "pd", "paddy_cake"]:
        assert library_ == "pandas"
    else:
        assert library_ == "numpy"
