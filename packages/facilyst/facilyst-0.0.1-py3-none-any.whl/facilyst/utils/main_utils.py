from facilyst.mock import Dates, Features, Target
from facilyst.mock.mock_types import handle_data_and_library_type


def create_data(
    data_type="features",
    library="pandas",
    num_rows=100,
    target_dtype="ints",
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

    :param data_type:
    :param library: The library of which the final dataset should be, options are 'pandas' and 'numpy'. Defaults to 'pandas'.
    :param num_rows: The number of observations in the final dataset. Defaults to 100.
    :param target_dtype: The data type that should be returned in the target. Options are 'ints', 'rand_ints', 'floats',
    'rand_floats', 'booleans', and 'categoricals'. Only used if the data_type is 'target'.
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
    :return:
    """
    kw_args = locals()
    data_type, library = handle_data_and_library_type(data_type, library)

    class_options = {"features": Features, "target": Target, "dates": Dates}

    all_kw_args = {k: v for k, v in kw_args if k not in ["data_type"]}

    if data_type == "target":
        class_args = {
            k: v for k, v in all_kw_args if k in ["library", "num_rows", "target_dtype"]
        }
    elif data_type == "dates":
        class_args = {k: v for k, v in all_kw_args if k in []}
    else:
        class_args = {k: v for k, v in all_kw_args if k not in ["target_dtype"]}

    data_class = class_options[data_type](**class_args)
    return data_class.get_data()
