from functools import singledispatch
from typing import Any

import pystac


@singledispatch
def get_items(stac: Any) -> None:
    """Take a sequence or collection of STAC items and return a list of item dictionaries."""
    raise ValueError(f"Unsupported type `{type(stac)}`.")


@get_items.register(pystac.Item)
def _get_items_from_item(stac):
    return [stac.to_dict()]


@get_items.register(dict)
def _get_items_from_item_dict(stac):
    return [stac]


@get_items.register(list)
def _get_items_from_list(stac):
    try:
        return [item.to_dict() for item in stac]
    except AttributeError:
        return [item for item in stac]


@get_items.register(pystac.ItemCollection)
def _get_items_from_collection(stac):
    return [item.to_dict() for item in stac]


@get_items.register(pystac.Catalog)
def _get_items_from_catalog(stac):
    return [item.to_dict() for item in stac.get_all_items()]
