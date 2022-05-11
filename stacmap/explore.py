from typing import List

import branca
import folium
import folium.plugins
import numpy as np

from stacmap.geojson import STACFeatureCollection
from stacmap.stac import get_items


def _basemap(tiles):
    m = folium.Map(tiles=tiles)
    folium.plugins.Fullscreen().add_to(m)
    return m


def _add_footprints_to_map(
    collection: STACFeatureCollection,
    m: folium.Map,
    fields=None,
    tooltip=True,
    popup=False,
    zoom_to=True,
    style_function=None,
    highlight_function=None,
):
    fields = fields if fields else collection.get_props()

    tooltip = folium.GeoJsonTooltip(fields) if tooltip else None
    popup = folium.GeoJsonPopup(fields) if popup else None

    geojson = folium.GeoJson(
        data=collection.to_dict(),
        tooltip=tooltip,
        popup=popup,
        name="Footprints",
        style_function=style_function,
        highlight_function=highlight_function,
    )

    if zoom_to:
        m.fit_bounds(geojson.get_bounds())

    geojson.add_to(m)


def _add_thumbnails_to_map(collection: STACFeatureCollection, m: folium.Map):
    features = collection.features
    thumbnails = folium.FeatureGroup(name="Thumbnails")

    for feat in features:
        try:
            url = feat.assets["thumbnail"]["href"]
        except KeyError:
            continue

        thumb_bounds = folium.GeoJson(feat.to_dict()).get_bounds()
        overlay = folium.raster_layers.ImageOverlay(url, bounds=thumb_bounds)
        overlay.add_to(thumbnails)

    thumbnails.add_to(m)


# TODO: Add item ID to tooltip/popup if possible
def explore(
    stac,
    *,
    bbox: List[float] = None,
    intersects: dict = None,
    prop: str = None,
    force_categorical: bool = False,
    cmap: str = None,
    highlight: bool = True,
    m: folium.Map = None,
    tiles: str = "OpenStreetMap",
    tooltip: bool = True,
    popup: bool = False,
    fields: List[str] = None,
    thumbnails: bool = False,
    zoom_to: bool = True,
) -> folium.Map:
    """Explore STAC items through an interactive map.

    Parameters
    ----------
    stac : STAC item or collection
        STAC items to explore.
    bbox : list of floats
        Bounding box coordinates (west, south, east, north) to overlay on the map.
    intersects : dict
        GeoJSON geometry to overlay on the map.
    prop : str, optional
        The STAC property to use for color-coding items.
    force_categorical : bool, default False
        If true, numeric properties are treated as categorical instead of continuous.
    cmap : str, optional
        The name of a colorbrewer colormap to apply. Ignored if no `prop` is given.
    highlight : bool, default True
        If True, highlight item footprints on hover.
    m : folium.Map
        Existing map instance on which to draw the plot. If none is provided, a new map will be created.
    tiles : str
        Map tileset to use. Can choose from the list supported by Folium.
    tooltip : bool, default True
        If True, item metadata will be displayed on hover.
    popup : bool, default False
        If True, item metadata will be displayed on click.
    fields : list
        A list of metadata fields to display in the tooltip or popup. If not provided, all shared fields are displayed.
        Ignored if `tooltip` and `popup` are `False`.
    thumbnails : bool, default False
        If true, thumbnails will be displayed on the map based on the `thumbnail` asset of each item.
    zoom_to : bool, default False
        If true, the map will zoom to the bounds of the items.
    """
    items = get_items(stac)
    fc = STACFeatureCollection(items)

    if m is None:
        m = _basemap(tiles)
        existing_map = False
    else:
        existing_map = True

    def style_function(x):
        return {
            "fillColor": x["properties"]["__stacmap_color"],
            "fillOpacity": 0.6,
            "color": x["properties"]["__stacmap_color"],
            "weight": 2.0,
        }

    def highlight_function(_):
        return {"fillOpacity": 0.9, "weight": 4.0} if highlight else None

    if prop is not None:
        values = fc.get_values(prop)
        categorical = not np.issubdtype(values.dtype, np.number)

        if categorical or force_categorical:
            cmap = cmap if cmap else "Set1"
            _set_categorical_colors(collection=fc, prop=prop, cmap=cmap, m=m)
        else:
            cmap = cmap if cmap else "RdBu_r"
            _set_continuous_colors(collection=fc, prop=prop, cmap=cmap, m=m)
    else:
        _set_fixed_color(fc, "#26bad1")

    if bbox is not None or intersects is not None:
        if bbox is not None and intersects is not None:
            raise ValueError("Cannot specify both `bbox` and `intersects`.")
        _add_search_bounds(m=m, bbox=bbox, intersects=intersects)

    _add_footprints_to_map(
        collection=fc,
        m=m,
        fields=fields,
        tooltip=tooltip,
        popup=popup,
        zoom_to=zoom_to,
        style_function=style_function,
        highlight_function=highlight_function,
    )

    if thumbnails is True:
        _add_thumbnails_to_map(fc, m)

    if not existing_map:
        folium.LayerControl(hideSingleBase=True, position="topleft").add_to(m)

    return m


def _add_search_bounds(m, bbox=None, intersects=None):
    if bbox is not None:
        w, s, e, n = bbox
        coords = [
            (w, s),
            (w, n),
            (e, n),
            (e, s),
            (w, s),
        ]
        geometry = dict(type="Polygon", coordinates=[coords])
    else:
        geometry = intersects

    bounds_style = {
        "fillOpacity": 0.1,
        "fillColor": "#000000",
        "color": "#6e6e6e",
        "weight": 1.0,
        "interactive": False,
    }

    geojson = folium.GeoJson(
        data=geometry, name="Bounds", style_function=lambda _: bounds_style
    )
    geojson.add_to(m)


def _set_continuous_colors(
    *, collection: STACFeatureCollection, prop: str, cmap: str, m: folium.Map
):
    """Set the `__stacmap_color` property of each item in the collection based on the
    continuous value of the given property. Add the continuous legend to the map."""
    features = collection.features
    base_colors = branca.utilities.color_brewer(cmap)
    colors = branca.utilities.linear_gradient(base_colors, 255)
    values = collection.get_values(prop)

    vmin = values.min()
    vmax = values.max()

    for feat in features:
        feat_value = feat.properties[prop]
        color_idx = (
            int(((feat_value - vmin) / (vmax - vmin)) * (len(colors) - 1))
            if vmax != vmin
            else 0
        )
        color = colors[color_idx]
        feat.properties["__stacmap_color"] = color

    _add_continous_legend(vmin=vmin, vmax=vmax, colors=colors, caption=prop, m=m)


def _set_categorical_colors(
    *, collection: STACFeatureCollection, prop: str, m: folium.Map, cmap: str = "Set1"
) -> None:
    """Set the `__stacmap_color` property of each item in the collection based on the
    categorical value of the given property. Add the categorical legend to the map"""
    colors = branca.utilities.color_brewer(cmap, 8)

    features = collection.features
    categories = []

    for feat in features:
        feat_value = feat.properties[prop]

        if feat_value not in categories:
            categories.append(feat_value)

        color_idx = categories.index(feat_value) % len(colors)
        color = colors[color_idx]
        feat.properties["__stacmap_color"] = color

    # Repeat colors to at least match the number of categories to avoid missing items in legend
    all_colors = colors * (len(categories) // len(colors) + 1)
    _add_categorical_legend(categories=categories, colors=all_colors, caption=prop, m=m)


def _set_fixed_color(collection: STACFeatureCollection, color):
    """Set the `__stacmap_color` property of each item in the collection to the given color."""
    features = collection.features

    for feat in features:
        feat.properties["__stacmap_color"] = color


def _add_continous_legend(vmin, vmax, colors, caption, m):
    """Add a continous legend color ramp to the map."""
    color_ramp = branca.colormap.LinearColormap(
        colors=colors, vmin=vmin, vmax=vmax, caption=caption
    )
    color_ramp.add_to(m)


def _add_categorical_legend(categories, colors, caption, m):
    """Add a categorical legend to the map.

    This implementation is written by Michel Metran (@michelmetran) and released on GitHub
    (https://github.com/michelmetran/package_folium) under MIT license.
    Copyright (c) 2020 Michel Metran

    Parameters
    ----------
    m : folium.Map
        Existing map instance on which to draw the plot
    title : str
        title of the legend (e.g. column name)
    categories : list-like
        list of categories
    colors : list-like
        list of colors (in the same order as categories)
    """
    head = """
    {% macro header(this, kwargs) %}
    <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
    <script>$( function() {
        $( ".maplegend" ).draggable({
            start: function (event, ui) {
                $(this).css({
                    right: "auto",
                    top: "auto",
                    bottom: "auto"
                });
            }
        });
    });
    </script>
    <style type='text/css'>
      .maplegend {
        position: absolute;
        z-index:9999;
        background-color: rgba(255, 255, 255, .8);
        border-radius: 5px;
        box-shadow: 0 0 15px rgba(0,0,0,0.2);
        padding: 10px;
        font: 12px/14px Arial, Helvetica, sans-serif;
        right: 10px;
        top: 20px;
      }
      .maplegend .legend-title {
        text-align: left;
        margin-bottom: 5px;
        font-weight: bold;
        }
      .maplegend .legend-scale ul {
        margin: 0;
        margin-bottom: 0px;
        padding: 0;
        float: left;
        list-style: none;
        }
      .maplegend .legend-scale ul li {
        list-style: none;
        margin-left: 0;
        line-height: 16px;
        margin-bottom: 2px;
        }
      .maplegend ul.legend-labels li span {
        display: block;
        float: left;
        height: 14px;
        width: 14px;
        margin-right: 5px;
        margin-left: 0;
        border: 0px solid #ccc;
        }
      .maplegend .legend-source {
        color: #777;
        clear: both;
        }
      .maplegend a {
        color: #777;
        }
    </style>
    {% endmacro %}
    """
    # Add CSS (on Header)
    macro = branca.element.MacroElement()
    macro._template = branca.element.Template(head)
    m.get_root().add_child(macro)

    body = f"""
    <div id='maplegend {caption}' class='maplegend'>
        <div class='legend-title'>{caption}</div>
        <div class='legend-scale'>
            <ul class='legend-labels'>"""

    # Loop Categories
    for label, color in zip(categories, colors):
        body += f"""
                <li><span style='background:{color}'></span>{label}</li>"""

    body += """
            </ul>
        </div>
    </div>
    """

    # Add Body
    body = branca.element.Element(body, "legend")
    m.get_root().html.add_child(body)
