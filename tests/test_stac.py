import pytest

from stacmap.stac import get_dict_from_item, get_items

from .stac_data import TEST_CATALOG, TEST_ITEM, TEST_ITEM_COLLECTION


def test_get_items_from_item():
    item_dict = get_items(TEST_ITEM)
    assert isinstance(item_dict, list)
    assert isinstance(item_dict[0], dict)


def test_get_items_from_item_dict():
    item_dict = get_items(TEST_ITEM.to_dict())
    assert isinstance(item_dict, list)
    assert isinstance(item_dict[0], dict)


def test_get_items_from_list_of_items():
    item_dict = get_items([TEST_ITEM, TEST_ITEM])
    assert isinstance(item_dict, list)
    assert isinstance(item_dict[0], dict)


def test_get_items_from_list_of_item_dicts():
    item_dict = get_items([TEST_ITEM.to_dict(), TEST_ITEM.to_dict()])
    assert isinstance(item_dict, list)
    assert isinstance(item_dict[0], dict)


def test_get_items_from_collection():
    item_dict = get_items(TEST_ITEM_COLLECTION)
    assert isinstance(item_dict, list)
    assert isinstance(item_dict[0], dict)


def test_get_items_from_catalog():
    item_dict = get_items(TEST_CATALOG)
    assert isinstance(item_dict, list)
    assert isinstance(item_dict[0], dict)


def test_get_items_from_non_stac():
    with pytest.raises(ValueError):
        get_items(4)


def test_get_dict_from_item_from_non_item():
    with pytest.raises(ValueError):
        get_dict_from_item(4)
