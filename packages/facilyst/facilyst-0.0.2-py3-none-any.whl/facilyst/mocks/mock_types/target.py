import pandas as pd

from facilyst.mocks import MockBase
from facilyst.mocks.mock_types.utils import mock_dtypes


class Target(MockBase):

    name = "Target"

    def __init__(self, library="pandas", num_rows=100, target_dtype="ints"):
        """

        :param library: The library of which the final data should be, options are 'pandas' and 'numpy'. Defaults to 'pandas'.
        :param num_rows: The number of observations in the final data. Defaults to 100.
        :param target_dtype: The data type that should be returned in the target. Options are 'ints', 'rand_ints', 'floats',
        'rand_floats', 'booleans', and 'categoricals'.
        """
        self.library = library.lower()

        parameters = {"target_dtype": target_dtype}

        super().__init__(library, num_rows, parameters)

    def create_data(self):
        final_output = self.handle_library()
        return final_output

    def handle_library(self):
        """
        Handles the library that was selected to determine the format in which the data will be returned, and then
        returns the data based on the dtype specified during class instantiation.

        :return: The final data created from the appropriate library as a pd.Series or ndarray.
        """
        dtype_to_keep = self.parameters["target_dtype"]
        mocked = Target._refine_dtypes(dtype_to_keep, self.num_rows)
        mocked_series = pd.Series(mocked, name=dtype_to_keep)

        if self.library.lower() == "pandas":
            return mocked_series
        elif self.library.lower() == "numpy":
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
