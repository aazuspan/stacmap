import sys

import pytest

from stacmap import utils


def test_cmap_branca():
    """Test that branca successfully retrieves a colorbrewer colormap"""
    # Force matplotlib import to fail
    sys.modules["matplotlib"] = None

    colors = utils.get_cmap("RdBu", 79)
    assert len(colors) == 79

    del sys.modules["matplotlib"]


def test_cmap_matplotlib():
    """Test that matplotlib succesfully retrieves a non-colorbrewer colormap"""
    colors = utils.get_cmap("viridis", 31)
    assert len(colors) == 31


def test_cmap_matplotlib_missing():
    """Test that an error is raised if a non-colorbrewer colormap is requested without matplotlib"""
    # Force matplotlib import to fail
    sys.modules["matplotlib"] = None

    with pytest.raises(ValueError):
        utils.get_cmap("viridis", 8)

    del sys.modules["matplotlib"]
