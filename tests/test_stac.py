import datetime

import pystac

from stacmap.stac import get_items

TEST_ITEM = pystac.Item(
    id="item1",
    geometry={"type": "Point", "coordinates": [0, 0]},
    bbox=[0, 0, 1, 1],
    datetime=datetime.datetime.now(),
    properties={"prop1": "value1"},
)

TEST_COLLECTION = pystac.ItemCollection([TEST_ITEM, TEST_ITEM])
TEST_CATALOG = pystac.Catalog(id="catalog1", description="Test catalog")
TEST_CATALOG.add_item(TEST_ITEM)


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
    item_dict = get_items(TEST_COLLECTION)
    assert isinstance(item_dict, list)
    assert isinstance(item_dict[0], dict)


def test_get_items_from_catalog():
    item_dict = get_items(TEST_CATALOG)
    assert isinstance(item_dict, list)
    assert isinstance(item_dict[0], dict)
