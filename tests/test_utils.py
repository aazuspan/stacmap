import pytest

from stacmap import utils

from .utils import mock_missing_import


def test_cmap_branca():
    """Test that branca successfully retrieves a colorbrewer colormap"""
    with mock_missing_import("matplotlib"):
        colors = utils.get_cmap("RdBu", 79)
        assert len(colors) == 79


def test_cmap_matplotlib():
    """Test that matplotlib succesfully retrieves a non-colorbrewer colormap"""
    colors = utils.get_cmap("viridis", 31)
    assert len(colors) == 31


def test_cmap_matplotlib_missing():
    """Test that an error is raised if a non-colorbrewer colormap is requested without matplotlib"""
    with mock_missing_import("matplotlib"):
        with pytest.raises(ValueError, match="pip install matplotlib"):
            utils.get_cmap("viridis", 18)
