"""File generated while packaging."""
import contextlib

version_info = {'short': '3.0.0', 'full': '3.0.0', 'release': True, 'clean': True, 'git revision': 'd71ae895f3f02b649781ddd047cff7dc7d4d5988'}
version_info['packaged'] = True
version = '3.0.0'


@contextlib.contextmanager
def hardcoded():
    """Dummy context manager, returns the version."""
    yield version
