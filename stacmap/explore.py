import copy
from typing import Any, Callable, Dict, List, Optional, Union

import branca  # type: ignore
import folium  # type: ignore
import folium.plugins  # type: ignore
import numpy as np
from numpy.typing import NDArray

from stacmap.geojson import STACFeatureCollection
from stacmap.stac import get_items
from stacmap.types import GeoJSON, ItemContainer, ItemDict
from stacmap.utils import get_cmap


def explore(
    stac: ItemContainer,
    *,
    name: Optional[str] = None,
    bbox: Optional[List[float]] = None,
    intersects: Optional[GeoJSON] = None,
    thumbnails: bool = False,
    prop: Optional[str] = None,
    cmap: Optional[str] = None,
    vmin: Optional[float] = None,
    vmax: Optional[float] = None,
    force_categorical: bool = False,
    tooltip: bool = True,
    popup: bool = False,
    fields: Optional[List[str]] = None,
    extensions: Optional[List[str]] = None,
    shared_fields: bool = False,
    add_id: bool = True,
    m: Optional[folium.Map] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    tiles: str = "OpenStreetMap",
    attr: Optional[str] = None,
    zoom_to: bool = True,
    legend: bool = True,
    layer_control: bool = True,
    highlight: bool = True,
    style_kwds: Dict[str, Any] = {},
    highlight_kwds: Dict[str, Any] = {},
    popup_kwds: Dict[str, Any] = {},
    tooltip_kwds: Dict[str, Any] = {},
    map_kwds: Dict[str, Any] = {},
) -> folium.Map:
    """Explore STAC items through an interactive map.

    Parameters
    ----------
    stac : STAC item or collection
        STAC items to explore.
    name : str, optional
        A name to assign to items in the layer control and legend. If no name is given, the
        `collection` property of the first STAC item will be used.
    bbox : list of floats
        Bounding box coordinates (west, south, east, north) to overlay on the map.
    intersects : dict
        GeoJSON geometry to overlay on the map.
    thumbnails : bool, default False
        If true, the `thumbnail` asset of each item will be displayed on the map.
    prop : str, optional
        The STAC property to use for color-coding items.
    cmap : str, optional
        The name of a colormap to apply for color-coding. By default, only `colorbrewer` colors are
        supported. Additional colors are available if `matplotlib` is installed.
    vmin : float, optional
        The minimum value for the color ramp. If none is given, it will be calculated from the
        `prop`.
    vmax : float, optional
        The maximum value for the color ramp. If none is given, it will be calculated from the
        `prop`.
    force_categorical : bool, default False
        If true, numeric properties are treated as categorical instead of continuous.
    tooltip : bool, default True
        If True, item metadata will be displayed on hover.
    popup : bool, default False
        If True, item metadata will be displayed on click.
    fields : list
        A list of metadata fields to display in the tooltip or popup. If not provided, all fields
        are displayed.
    extensions : list
        A list of STAC extension field prefixes (like `eo` or `proj`) to include in the tooltip or
        popup. If not provided, all extensions will be included. Base STAC properties will be
        included regardless.
    shared_fields: bool, default False
        If true, only fields shared by all items will be displayed in the tooltip or popup.
        Otherwise, missing fields will be populated with `None`.
    add_id : bool, default True
        If true, the STAC `id` of each item will be added to its properties in the tooltip and
        popup.
    m : folium.Map
        Existing :external:class:`~folium.folium.Map` instance on which to draw the plot. If none is
        provided, a new map will be created.
    width : int, optional
        Width of the map in pixels.
    height : int, optional
        Height of the map in pixels.
    tiles : str
        Map tileset to use, supported by :external:class:`~folium.folium.Map`.
    attr : str, optional
        Attribution information for custom tile sets.
    zoom_to : bool, default False
        If true, the map will zoom to the bounds of the items.
    legend : bool, default True
        Whether to show a legend for the color ramp.
    layer_control : bool, default True
        Whether to show the layer control.
    highlight : bool, default True
        Whether to highlight items on hover.
    style_kwds: dict, default {}
        Additional styles to be passed to the `style_function` of
        :external:class:`~folium.features.GeoJson`. If `prop` is provided, `color` and `fillColor`
        will be set automatically and override options passed to `style_kwds`.
    highlight_kwds: dict, default {}
        Additional styles to be passed to the `highlight_function` of
        :external:class:`~folium.features.GeoJson`.
    tooltip_kwds: dict, default {}
        Additional styles to be passed to :external:class:`~folium.features.GeoJsonTooltip`.
    popup_kwds: dict, default {}
        Additional styles to be passed to :external:class:`~folium.features.GeoJsonPopup`.
    map_kwds: dict, default {}
        Additional styles to be passed to :external:class:`~folium.folium.Map`, if an existing map
        `m` is not given.

    Returns
    -------
    folium.Map
        The :external:class:`~folium.folium.Map` instance.

    Examples
    --------
    >>> import stacmap, pystac
    >>> catalog = pystac.Catalog.from_file(
        "https://planet.com/data/stac/disasters/hurricane-harvey/hurricane-harvey-0831/catalog.json"
    )
    >>> stacmap.explore(catalog, prop="gsd", force_categorical=True)
    """
    items = copy.deepcopy(get_items(stac))
    if len(items) == 0:
        raise ValueError("No STAC items were found.")

    fc = STACFeatureCollection(items)
    name = name if name is not None else items[0]["collection"]
    highlight_kwds["fillOpacity"] = highlight_kwds.get("fillOpacity", 0.75)

    if m is None:
        m = _basemap(tiles=tiles, attr=attr, width=width, height=height, map_kwds=map_kwds)
    else:
        # Adding layers to a map that already contains a layer control causes rendering issues.
        # To prevent that, we manually remove the layer control and add it back later.
        layer_controls = [k for k in m._children.keys() if k.startswith("layer_control")]
        [m._children.pop(lc) for lc in layer_controls]

    def style_function(x: ItemDict) -> Dict[str, Any]:
        item_style = style_kwds.copy()

        if prop is not None:
            item_style["color"] = x["properties"]["__stacmap_color"]
            item_style["fillColor"] = x["properties"]["__stacmap_color"]

        return item_style

    def highlight_function(_: ItemDict) -> Dict[str, Any]:
        if highlight is False:
            return {}

        return highlight_kwds

    if prop is not None:
        values = fc.get_values(prop)
        categorical = force_categorical is True or not np.issubdtype(values.dtype, np.number)

        if categorical:
            categories = np.unique(values)

            cmap = cmap if cmap else "Set1"
            n_colors = len(categories)
            colors = get_cmap(cmap, n_colors)

            _set_categorical_colors(collection=fc, prop=prop, colors=colors)

            if legend is True:
                _add_categorical_legend(
                    categories=categories, colors=colors, caption=f"{name}: {prop}", m=m
                )
        else:
            vmin = vmin if vmin is not None else values.min()
            vmax = vmax if vmax is not None else values.max()

            cmap = cmap if cmap else "RdBu_r"
            n_colors = 255
            colors = get_cmap(cmap, n_colors)

            _set_continuous_colors(
                collection=fc,
                prop=prop,
                colors=colors,
                vmin=vmin,
                vmax=vmax,
            )

            if legend is True:
                _add_continuous_legend(
                    vmin=vmin, vmax=vmax, colors=colors, caption=f"{name}: {prop}", m=m
                )

    if bbox is not None or intersects is not None:
        if bbox is not None and intersects is not None:
            raise ValueError("Cannot specify both `bbox` and `intersects`.")
        _add_search_bounds(m=m, name=name, bbox=bbox, intersects=intersects)

    _add_footprints_to_map(
        collection=fc,
        m=m,
        name=name,
        fields=fields,
        extensions=extensions,
        shared_fields=shared_fields,
        tooltip=tooltip,
        popup=popup,
        zoom_to=zoom_to,
        style_function=style_function,
        highlight_function=highlight_function,
        popup_kwds=popup_kwds,
        tooltip_kwds=tooltip_kwds,
        add_id=add_id,
    )

    if thumbnails is True:
        _add_thumbnails_to_map(fc, m, name=name)

    # LayerControl must be added after all layers are added to the map
    # https://github.com/python-visualization/folium/issues/1553
    if layer_control is True:
        folium.LayerControl(hideSingleBase=True, position="topleft").add_to(m)

    return m


def _basemap(
    tiles: str,
    attr: Optional[str],
    width: Optional[Union[str, int]],
    height: Optional[Union[str, int]],
    map_kwds: Optional[Dict[str, Any]],
) -> folium.Map:
    # folium.Map fails with None as width or height, so only pass if they are not None
    size_kwds = {}
    if width is not None:
        size_kwds["width"] = width
    if height is not None:
        size_kwds["height"] = height

    m = folium.Map(tiles=tiles, attr=attr, **size_kwds, **map_kwds)
    folium.plugins.Fullscreen().add_to(m)
    return m


def _add_footprints_to_map(
    collection: STACFeatureCollection,
    m: folium.Map,
    name: str,
    fields: Optional[List[str]],
    extensions: Optional[List[str]],
    shared_fields: bool,
    tooltip: bool,
    popup: bool,
    zoom_to: bool,
    style_function: Callable[[ItemDict], Dict[str, Any]],
    highlight_function: Callable[[ItemDict], Dict[str, Any]],
    add_id: bool,
    popup_kwds: Dict[str, Any],
    tooltip_kwds: Dict[str, Any],
) -> None:
    if fields is None:
        fields = (
            collection.get_all_props() if shared_fields is False else collection.get_shared_props()
        )

    if add_id is True:
        fields = ["id"] + fields
        for feature in collection.features:
            if "id" in feature.properties:
                continue
            feature.properties = {"id": feature.id, **feature.properties}

    # Filter by field extensions
    if extensions is not None:
        keep_fields = []
        for field in fields:
            split = field.split(":")
            if len(split) == 1 or split[0] in extensions:
                keep_fields.append(field)
        fields = keep_fields

    # Populate all missing fields with None to avoid tooltip errors
    if shared_fields is False:
        for feature in collection.features:
            for field in fields:
                if field in feature.properties:
                    continue
                feature.properties[field] = None

    tooltip = folium.GeoJsonTooltip(fields, **tooltip_kwds) if tooltip else None
    popup = folium.GeoJsonPopup(fields, **popup_kwds) if popup else None

    geojson = folium.GeoJson(
        data=collection.to_dict(),
        tooltip=tooltip,
        popup=popup,
        name=f"{name} - Footprints",
        style_function=style_function,
        highlight_function=highlight_function,
    )

    if zoom_to:
        m.fit_bounds(geojson.get_bounds())

    geojson.add_to(m)


def _add_thumbnails_to_map(collection: STACFeatureCollection, m: folium.Map, name: str) -> None:
    features = collection.features
    thumbnails = folium.FeatureGroup(name=f"{name} - Thumbnails")

    for feat in features:
        try:
            url = feat.assets["thumbnail"]["href"]
        except KeyError:
            continue

        thumb_bounds = folium.GeoJson(feat.to_dict()).get_bounds()
        overlay = folium.raster_layers.ImageOverlay(url, bounds=thumb_bounds)
        overlay.add_to(thumbnails)

    if len(thumbnails._children) == 0:
        raise ValueError("Items do not have thumbnail links.")

    thumbnails.add_to(m)


def _add_search_bounds(
    m: folium.Map, name: str, bbox: Optional[List[float]], intersects: Optional[GeoJSON]
) -> None:
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
    elif intersects is not None:
        geometry = intersects

    bounds_style = {
        "fill": False,
        "interactive": False,
    }

    geojson = folium.GeoJson(
        data=geometry, name=f"{name} - Bounds", style_function=lambda _: bounds_style
    )
    geojson.add_to(m)


def _set_continuous_colors(
    *,
    collection: STACFeatureCollection,
    prop: str,
    colors: NDArray[np.unicode_],
    vmin: float,
    vmax: float,
) -> None:
    """Set the `__stacmap_color` property of each item in the collection based on the
    continuous value of the given property."""
    features = collection.features
    n_colors = len(colors)

    for feat in features:
        feat_value = feat.properties[prop]
        color_idx = (
            int(((feat_value - vmin) / (vmax - vmin)) * (n_colors - 1)) if vmax != vmin else 0
        )
        # Clamp the index to avoid index errors that may occur with custom vmin and vmax
        color_idx = max(0, min(color_idx, n_colors - 1))

        color = colors[color_idx]
        feat.properties["__stacmap_color"] = color


def _set_categorical_colors(
    *, collection: STACFeatureCollection, prop: str, colors: NDArray[np.unicode_]
) -> None:
    """Set the `__stacmap_color` property of each item in the collection based on the
    categorical value of the given property. Add the categorical legend to the map"""
    features = collection.features
    categories = np.unique(collection.get_values(prop))

    for feat in features:
        feat_value = feat.properties[prop]
        color = colors[np.where(categories == feat_value)[0][0]]
        feat.properties["__stacmap_color"] = color


def _add_continuous_legend(
    vmin: float, vmax: float, colors: NDArray[np.unicode_], caption: str, m: folium.Map
) -> branca.colormap.LinearColormap:
    """Add a continuous legend color ramp to the map."""
    color_ramp = branca.colormap.LinearColormap(
        colors=colors, vmin=vmin, vmax=vmax, caption=caption
    )
    color_ramp.add_to(m)
    return color_ramp


def _add_categorical_legend(
    categories: NDArray[np.unicode_],
    colors: NDArray[np.unicode_],
    caption: str,
    m: folium.Map,
) -> branca.element.MacroElement:
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

    legend_items = "\n".join(
        [
            f"<li><span style='background:{color}'></span>{label}</li>"
            for color, label in zip(colors, categories)
        ]
    )

    legend_body = f"""
    <div id='maplegend {caption}' class='maplegend'>
        <div class='legend-title'>{caption}</div>
        <div class='legend-scale'>
            <ul class='legend-labels'>
                {legend_items}
            </ul>
        </div>
    </div>
    """

    legend = branca.element.Element(legend_body, "legend")

    m.get_root().html.add_child(legend)

    return legend
