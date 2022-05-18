from typing import Any, Dict, List, Union

import pystac

GeoJSON = Dict[str, Any]
ItemDict = Dict[str, Any]
ItemList = List[ItemDict]
ItemLike = Union[pystac.Item, ItemDict]
ItemLikeList = List[ItemLike]
ItemContainer = Union[pystac.ItemCollection, pystac.Catalog, ItemLikeList, ItemLike]
