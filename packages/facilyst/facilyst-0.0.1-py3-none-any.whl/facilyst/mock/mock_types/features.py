import pandas as pd

from facilyst.mock.mock_types import MockBase
from facilyst.mock.mock_types.utils import mock_dtypes


class Features(MockBase):
    def __init__(
        self,
        library="pandas",
        num_rows=100,
        ints=True,
        rand_ints=True,
        floats=True,
        rand_floats=True,
        booleans=False,
        categoricals=False,
        dates=False,
        texts=False,
        ints_with_na=False,
        floats_with_na=False,
        all_dtypes=False,
    ):
        """

        :param library: The library of which the final dataset should be, options are 'pandas' and 'numpy'. Defaults to 'pandas'.
        :param num_rows: The number of observations in the final dataset. Defaults to 100.
        :param ints: Flag that includes column with monotonically increasing incremental set of negative and positive integers. Defaults to True.
        :param rand_ints: Flag that includes column with randomly selected integers between -5 and 5. Defaults to True.
        :param floats: Flag that includes column which is the float version of the 'ints' column. Defaults to True.
        :param rand_floats: Flag that includes column with randomly selected floats between -5 and 5. Defaults to True.
        :param booleans: Flag that includes column with randomly selected boolean values. Defaults to False.
        :param categoricals: Flag that includes column with four categoriesL 'First', 'Second', 'Third', and 'Fourth'. Defaults to False.
        :param dates: Flag that includes column with monotonically increasing dates from 01/01/2001 with a daily frequency. Defaults to False.
        :param texts: Flag that includes column with different text on each line. Defaults to False.
        :param ints_with_na: Flag that includes column which is the same as the 'ints' column with pd.NA included. Defaults to False.
        :param floats_with_na: Flag that includes column which is the same as the 'floats' column with pd.NA included. Defaults to False.
        :param all_dtypes: Flag that includes all columns. Defaults to False.
        """
        kw_args = locals()
        self.library = library

        if all_dtypes:
            parameters = {
                k: v for k, v in kw_args if k not in ["self", "library", "num_rows"]
            }
        else:
            parameters = {
                k: v
                for k, v in kw_args
                if k not in ["self", "library", "num_rows"] and v
            }

        super().__init__(num_rows, parameters)

    def create_data(self):
        self.final_output = self.handle_library()

    def handle_library(self):
        """
        Handles the library that was selected to determine the format in which the data will be returned, and then
        returns the data based on the dtypes specified during class instantiation.

        :return: The final data created from the appropriate library as a pd.DataFrame or ndarray.
        """
        dtypes_to_keep = list(self.parameters.keys())
        mocked = Features._refine_dtypes(dtypes_to_keep, self.num_rows)

        mocked_df = pd.DataFrame.from_dict(mocked)

        if self.library == "pandas":
            if "ints_with_na" in dtypes_to_keep:
                mocked_df["ints_with_na"] = mocked_df["ints_with_na"].astype("Int64")
            if "floats_with_na" in dtypes_to_keep:
                mocked_df["floats_with_na"] = mocked_df["floats_with_na"].astype(
                    "Float64"
                )
            return mocked_df
        elif self.library == "numpy":
            return mocked_df.to_numpy()

        return mocked_df

    @staticmethod
    def _refine_dtypes(dtypes=None, num_rows=100):
        """
        Internal function that selects the dtypes to be kept from the full dataset.

        :param dtypes: All data format options from the class initialization. Defaults to returning the full dataset.
        :param num_rows : The number of observations in the final dataset. Defaults to 100.
        :return: A refined form of the full set of columns available.
        """
        full_mock = mock_dtypes(num_rows)
        if dtypes:
            return {k: v for k, v in full_mock.items() if k in dtypes}
        else:
            return full_mock
