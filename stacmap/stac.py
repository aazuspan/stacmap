from functools import singledispatch
from typing import Union

import pystac

from stacmap.types import ItemContainer, ItemDict, ItemLike, ItemLikeList, ItemList


@singledispatch
def get_items(stac: Union[ItemLike, ItemContainer]) -> ItemList:
    """Take a sequence or collection of STAC items and return a list of item dictionaries."""
    raise ValueError(f"Unsupported type `{type(stac)}`.")


@get_items.register(pystac.Item)
def _get_items_from_item(stac: pystac.Item) -> ItemList:
    return [stac.to_dict()]


@get_items.register(dict)
def _get_items_from_item_dict(stac: ItemDict) -> ItemList:
    return [stac]


@get_items.register(list)
def _get_items_from_list(stac: ItemLikeList) -> ItemList:
    return [get_dict_from_item(item) for item in stac]


@get_items.register(pystac.ItemCollection)
def _get_items_from_collection(stac: pystac.ItemCollection) -> ItemList:
    return [item.to_dict() for item in stac]


@get_items.register(pystac.Catalog)
def _get_items_from_catalog(stac: pystac.Catalog) -> ItemList:
    return [item.to_dict() for item in stac.get_all_items()]


@singledispatch
def get_dict_from_item(item: ItemLike) -> ItemDict:
    """Take a STAC item and return an item dictionary."""
    raise ValueError(f"Unsupported type `{type(item)}`.")


@get_dict_from_item.register(pystac.Item)
def _get_dict_from_pystac_item(item: pystac.Item) -> ItemDict:
    return item.to_dict()


@get_dict_from_item.register(dict)
def _get_dict_from_dict(item: ItemDict) -> ItemDict:
    return item
