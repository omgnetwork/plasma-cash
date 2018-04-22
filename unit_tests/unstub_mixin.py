import pytest
from mockito import unstub


class UnstubMixin(object):
    """This a helper mixin to automatically unstub after each test call"""
    @pytest.fixture(autouse=True)
    def unstub(self):
        yield
        unstub()
