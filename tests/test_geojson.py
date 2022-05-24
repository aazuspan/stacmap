import pytest

from stacmap.geojson import STACFeatureCollection
from stacmap.stac import get_items

from .stac_data import TEST_ITEM_COLLECTION


def test_len():
    items = get_items(TEST_ITEM_COLLECTION)
    fc = STACFeatureCollection(items)
    assert len(fc) == 5
