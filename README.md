# stacmap

Create interactive maps of [STAC](https://stacspec.org/) items.

# Features

- 🗺️ Explore STAC item footprints
- 🌈 Color-code items by properties
- 🖼️ Preview item thumbnails
- 🪶 Lightweight, minimal dependencies (just `folium` and `pystac`)

# Installation

```bash
$ pip install stacmap
```

# Quickstart

`stacmap.explore` creates an interactive [Folium](https://python-visualization.github.io/folium/) map from STAC items or collections.

```python
import stacmap
from pystac_client import Client

# Find Landsat Collection 2 scenes over an area of interest
catalog = Client.open("https://landsatlook.usgs.gov/stac-server")
items = catalog.search(
    bbox=[-120.9519, 37.2455, -113.4812, 45.1025],
    collections=["landsat-c2l2-sr"],
    datetime="2019-08-01/2019-08-03"
).get_all_items()


# Plot the items on an interactive map
stacmap.explore(items)
```

Color-code items by property by passing a `prop`:

```python
stacmap.explore(items, prop="eo:cloud_cover")
```

Draw the search bounding box with `bbox`:

```python
stacmap.explore(items, bbox=[-120.9519, 37.2455, -113.4812, 45.1025])
```