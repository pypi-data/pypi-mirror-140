from facilyst.mocks import MockBase
from facilyst.utils.gen_utils import _get_subclasses


def _all_mock_data_types():
    return _get_subclasses(MockBase)
