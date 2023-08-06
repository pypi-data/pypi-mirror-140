from abc import ABC, abstractmethod


class MockBase(ABC):
    def __init__(self, library=None, num_rows=100, parameters=None):
        self.library = library
        self.num_rows = num_rows
        self.parameters = parameters

    @property
    @abstractmethod
    def name(self):
        """Name of the mock type"""

    @abstractmethod
    def create_data(self):
        """Abstract method to be called by child classes to create the final data"""

    def get_data(self):
        """Returns the final data"""
        return self.create_data()
