from facilyst.utils import create_data


def test_create_data_default():
    data = create_data()


def test_create_data_target():
    data = create_data(data_type="target")
