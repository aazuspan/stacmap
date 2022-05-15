import sys
from contextlib import contextmanager


@contextmanager
def mock_missing_import(module_name):
    """Force a module to raise ImportError when imported. On exit,
    return the module to its original state."""
    module = sys.modules.get(module_name)
    sys.modules[module_name] = None

    try:
        yield
    finally:
        if module is None:
            del sys.modules[module_name]
        else:
            sys.modules[module_name] = module
