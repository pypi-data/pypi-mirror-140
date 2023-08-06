import pandas as pd

from facilyst.mock.mock_types import MockBase
from facilyst.mock.mock_types.utils import mock_dtypes


class Target(MockBase):
    def __init__(self, library="pandas", num_rows=100, dtype="ints"):
        """

        :param library: The library of which the final data should be, options are 'pandas' and 'numpy'. Defaults to 'pandas'.
        :param num_rows: The number of observations in the final data. Defaults to 100.
        :param dtype: The data type that should be returned in the target. Options are 'ints', 'rand_ints', 'floats',
        'rand_floats', 'booleans', and 'categoricals'.
        """
        self.library = library

        parameters = {"dtype": dtype}

        super().__init__(num_rows, parameters)

    def create_data(self):
        self.final_output = self.handle_library()

    def handle_library(self):
        """
        Handles the library that was selected to determine the format in which the data will be returned, and then
        returns the data based on the dtype specified during class instantiation.

        :return: The final data created from the appropriate library as a pd.Series or ndarray.
        """
        dtype_to_keep = self.parameters["dtype"]
        mocked = Target._refine_dtypes(dtype_to_keep, self.num_rows)

        mocked_series = pd.DataFrame.from_dict(mocked)[f"{dtype_to_keep}"]

        if self.library == "pandas":
            return mocked_series
        elif self.library == "numpy":
            return mocked_series.to_numpy()

        return mocked_series

    @staticmethod
    def _refine_dtypes(dtype="ints", num_rows=100):
        """
        Internal function that selects the dtype to be kept from the full dataset.

        :param dtype: The data type selected from the class initialization. Defaults to returning 'ints'.
        :param num_rows : The number of observations in the final target set. Defaults to 100.
        :return: A target data set of one data type.
        """
        full_mock = mock_dtypes(num_rows)
        if dtype:
            return full_mock[f"{dtype}"]
        else:
            return full_mock["ints"]
