from collections import Counter
from typing import Hashable, List

import numpy as np

HIDDEN_PROPS = ["__stacmap_color"]


class STACFeatureCollection:
    """A collection of STACFeatures."""

    def __init__(self, items: List[dict]):
        self.type = "FeatureCollection"
        self.features = [STACFeature(item) for item in items]

    def to_dict(self) -> dict:
        d = self.__dict__.copy()
        d.update({"features": [feat.to_dict() for feat in self.features]})
        return d

    def __len__(self):
        return len(self.features)

    def get_props(self) -> List[str]:
        """Return a list of properties that are common to all features."""
        props = Counter()

        for feat in self.features:
            props.update(feat.properties.keys())

        return [
            k
            for k, v in props.items()
            if v == len(self.features) and k not in HIDDEN_PROPS
        ]

    def get_values(self, prop: str) -> np.array:
        """Get all feature values for a given property."""
        props = self.get_props()

        if prop not in props:
            raise ValueError(
                f"Not all items have the property `{prop}`. Choose from `{props}`."
            )
        return np.array([feature.get_value(prop) for feature in self.features])


class STACFeature:
    """A GeoJSON Feature derived from a STAC item dictionary."""

    def __init__(self, item: dict):
        self.type = "Feature"
        self.id = item.get("id", None)
        self.properties = item.get("properties", {})
        self.geometry = item.get("geometry", {})
        self.bbox = item.get("bbox", {})
        self.assets = item.get("assets", {})

    def to_dict(self) -> dict:
        return self.__dict__

    def get_value(self, prop: str) -> Hashable:
        return self.properties[prop]
