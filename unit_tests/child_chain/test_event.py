from mockito import ANY, mock, verify, when

from plasma_cash.child_chain.event import emit, on
from unit_tests.unstub_mixin import UnstubMixin

handler = None


@on('simple')
def simple_handler():
    handler()


@on('args')
def args_handler(*args, **kwargs):
    handler(*args, **kwargs)


class TestEvent(UnstubMixin):

    def test_simple(self):
        global handler
        handler = mock()
        when(handler).__call__().thenReturn(None)
        emit('simple')
        verify(handler).__call__()

    def test_args(self):
        DUMMY_ARGS = [1, 2, 3]
        DUMMY_KWARGS = {'a': 1, 'b': 2, 'c': 3}

        global handler
        handler = mock()
        when(handler).__call__(ANY).thenReturn(None)
        emit('args', *DUMMY_ARGS, **DUMMY_KWARGS)
        verify(handler).__call__(*DUMMY_ARGS, **DUMMY_KWARGS)
