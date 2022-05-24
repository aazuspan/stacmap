import copy

import pystac
import pytest

import stacmap

from .stac_data import TEST_ITEM, TEST_ITEM_COLLECTION


def _fetch_map_string(m):
    """https://github.com/geopandas/geopandas/blob/main/geopandas/tests/test_explore.py"""
    out = m._parent.render()
    return out


def _get_first_child(m, name):
    """Get the first child element from a map that starts with a name substring"""
    for child in m._children:
        if child.startswith(name):
            return m._children[child]
    return None


def test_continuous_prop():
    m = stacmap.explore(
        TEST_ITEM_COLLECTION, prop="eo:cloud_cover", vmin=4, vmax=20, name="TEST DATA"
    )
    m.render()

    layer_control = _get_first_child(m, "layer_control")
    assert "TEST DATA - Footprints" in layer_control.overlays

    legend = _get_first_child(m, "color_map")
    assert legend is not None
    assert legend.vmin == 4
    assert legend.vmax == 20
    assert legend.caption == "TEST DATA: eo:cloud_cover"


def test_categorical_prop():
    m = stacmap.explore(TEST_ITEM_COLLECTION, prop="eo:cloud_cover", force_categorical=True)
    m.render()

    layer_control = _get_first_child(m, "layer_control")
    assert "planet-disaster-data - Footprints" in layer_control.overlays

    html = _fetch_map_string(m)
    assert "<div class='legend-title'>planet-disaster-data: eo:cloud_cover</div>" in html
    assert "<li><span style='background:#e41a1c'></span>0</li>" in html


def test_no_legend():
    m = stacmap.explore(TEST_ITEM_COLLECTION, prop="eo:cloud_cover", legend=False)
    m.render()

    html = _fetch_map_string(m)
    assert "<div class='legend-title'>planet-disaster-data: eo:cloud_cover</div>" not in html


def test_existing_map():
    m = stacmap.explore(TEST_ITEM_COLLECTION, name="DATA 1")
    m = stacmap.explore(TEST_ITEM_COLLECTION, name="DATA 2", m=m)
    m.render()

    layer_control = _get_first_child(m, "layer_control")
    assert "DATA 1 - Footprints" in layer_control.overlays
    assert "DATA 2 - Footprints" in layer_control.overlays


def test_map_kwds():
    m = stacmap.explore(TEST_ITEM_COLLECTION, width=300, height=150, map_kwds={"zoomStart": 14})
    assert m.width[0] == 300.0
    assert m.height[0] == 150.0
    assert m.options["zoomStart"] == 14


def test_bbox():
    bbox = (0, 0, 30, 30)
    m = stacmap.explore(TEST_ITEM_COLLECTION, name="LAYER", bbox=bbox)
    m.render()

    layer_control = _get_first_child(m, "layer_control")
    assert "LAYER - Bounds" in layer_control.overlays


def test_intersects():
    intersects = dict(type="Point", coordinates=[125.6, 10.1])
    m = stacmap.explore(TEST_ITEM_COLLECTION, name="LAYER", intersects=intersects)
    m.render()

    layer_control = _get_first_child(m, "layer_control")
    assert "LAYER - Bounds" in layer_control.overlays


def test_bbox_and_intersects():
    bbox = (0, 0, 30, 30)
    intersects = dict(type="Point", coordinates=[125.6, 10.1])

    with pytest.raises(ValueError, match="Cannot specify both"):
        stacmap.explore(TEST_ITEM_COLLECTION, bbox=bbox, intersects=intersects)


def test_highlight():
    m = stacmap.explore(TEST_ITEM_COLLECTION, highlight=False)
    layer = _get_first_child(m, "geo_json")
    assert layer.highlight_function(None) == {}

    highlight_kwds = {"fillOpacity": 0.9, "stroke": False}
    m = stacmap.explore(TEST_ITEM_COLLECTION, highlight_kwds=highlight_kwds)
    layer = _get_first_child(m, "geo_json")
    assert layer.highlight_function(None) == highlight_kwds


def test_style():
    style_kwds = {"color": "red", "fillOpacity": 0.9, "stroke": False}
    m = stacmap.explore(TEST_ITEM_COLLECTION, style_kwds=style_kwds)
    layer = _get_first_child(m, "geo_json")
    assert layer.style_function(None) == style_kwds

    # Prop-derived color should overwrite `color` and `fillColor` in style_kwds
    style_kwds = {"color": "red", "fillOpacity": 0.9, "stroke": False}
    m = stacmap.explore(TEST_ITEM_COLLECTION, prop="eo:cloud_cover", style_kwds=style_kwds)
    layer = _get_first_child(m, "geo_json")
    item = copy.deepcopy(TEST_ITEM.to_dict())
    item["properties"]["__stacmap_color"] = "cyan"

    assert layer.style_function(item)["color"] == "cyan"
    assert layer.style_function(item)["fillColor"] == "cyan"


def test_tooltip_and_popup():
    m = stacmap.explore(TEST_ITEM_COLLECTION)
    layer = _get_first_child(m, "geo_json")
    tooltip = _get_first_child(layer, "geo_json_tooltip")
    popup = _get_first_child(layer, "geo_json_popup")
    assert tooltip is not None
    assert popup is None

    m = stacmap.explore(TEST_ITEM_COLLECTION, tooltip=False, popup=True)
    layer = _get_first_child(m, "geo_json")
    tooltip = _get_first_child(layer, "geo_json_tooltip")
    popup = _get_first_child(layer, "geo_json_popup")
    assert tooltip is None
    assert popup is not None

    m = stacmap.explore(TEST_ITEM_COLLECTION, tooltip_kwds={"sticky": True})
    layer = _get_first_child(m, "geo_json")
    tooltip = _get_first_child(layer, "geo_json_tooltip")
    assert tooltip.tooltip_options["sticky"] == True


def test_fields():
    fields = ["eo:cloud_cover", "view:off_nadir"]
    m = stacmap.explore(TEST_ITEM_COLLECTION, fields=fields)
    layer = _get_first_child(m, "geo_json")
    tooltip = _get_first_child(layer, "geo_json_tooltip")

    assert tooltip.fields == ["id"] + fields


def test_extensions():
    extensions = ["eo"]
    m = stacmap.explore(TEST_ITEM_COLLECTION, extensions=extensions)
    layer = _get_first_child(m, "geo_json")
    tooltip = _get_first_child(layer, "geo_json_tooltip")
    assert tooltip.fields == [
        "id",
        "constellation",
        "created",
        "datetime",
        "gsd",
        "instruments",
        "platform",
        "updated",
        "eo:cloud_cover",
    ]


def test_shared_fields():
    m = stacmap.explore(TEST_ITEM_COLLECTION, shared_fields=True)
    layer = _get_first_child(m, "geo_json")
    tooltip = _get_first_child(layer, "geo_json_tooltip")
    assert "constellation" not in tooltip.fields

    m = stacmap.explore(TEST_ITEM_COLLECTION, shared_fields=False)
    layer = _get_first_child(m, "geo_json")
    tooltip = _get_first_child(layer, "geo_json_tooltip")
    assert "constellation" in tooltip.fields


def test_tiles():
    m = stacmap.explore(TEST_ITEM_COLLECTION, tiles="cartodbpositron")
    tiles = _get_first_child(m, "cartodbpositron")
    assert tiles is not None

    with pytest.raises(ValueError, match="must have an attribution"):
        stacmap.explore(TEST_ITEM_COLLECTION, tiles="notrealtiles")
    stacmap.explore(TEST_ITEM_COLLECTION, tiles="notrealtiles", attr="attr text")


def test_empty_stac():
    with pytest.raises(ValueError, match="No STAC items were found"):
        stacmap.explore(pystac.ItemCollection(items=[]))


def test_thumbnails():
    m = stacmap.explore(TEST_ITEM, thumbnails=True, name="LAYER")
    m.render()
    layer_control = _get_first_child(m, "layer_control")
    assert "LAYER - Thumbnails" in layer_control.overlays

    test_item = copy.deepcopy(TEST_ITEM.to_dict())
    del test_item["assets"]["thumbnail"]
    with pytest.raises(ValueError, match="do not have thumbnail links"):
        stacmap.explore(test_item, thumbnails=True)


def test_add_id():
    # The `id` property should be automatically populated from the STAC ID
    test_item = copy.deepcopy(TEST_ITEM.to_dict())
    m = stacmap.explore(test_item, name="LAYER")
    layer = _get_first_child(m, "geo_json")
    assert layer.data["features"][0]["properties"]["id"] == "20170831_172754_101c"

    # Using `add_id=False` should prevent an ID property from being added
    test_item = copy.deepcopy(TEST_ITEM.to_dict())
    m = stacmap.explore(test_item, name="LAYER", add_id=False)
    layer = _get_first_child(m, "geo_json")
    assert "id" not in layer.data["features"][0]["properties"]

    # If an item already has an ID property, it shouldn't be overwritten
    test_item = copy.deepcopy(TEST_ITEM.to_dict())
    test_item["properties"]["id"] = "MY CUSTOM ID"

    m = stacmap.explore(test_item, name="LAYER")
    layer = _get_first_child(m, "geo_json")
    assert layer.data["features"][0]["properties"]["id"] == "MY CUSTOM ID"


def test_layer_control():
    m = stacmap.explore(TEST_ITEM_COLLECTION)
    layer = _get_first_child(m, "layer_control")
    assert layer is not None

    m = stacmap.explore(TEST_ITEM_COLLECTION, layer_control=False)
    layer = _get_first_child(m, "layer_control")
    assert layer is None
