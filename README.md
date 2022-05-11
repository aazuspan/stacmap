# stacmap

Create interactive maps of [STAC]() items.

# Features

- 🗺️ Explore STAC item footprints
- 🌈 Color-code items by properties
- 🖼️ Preview item thumbnails
- 🪶 Lightweight, minimal dependencies (just `folium` and `pystac`)

# Installation

```bash
pip install stacmap
```

# Quickstart

`stacmap.explore` creates an interactive [Folium]() map from STAC items or collections.

```python
import stacmap
from pystac_client import Client

# Find Sentinel-2 scenes over an area of interest
catalog = Client.open("https://earth-search.aws.element84.com/v0")
items = catalog.search(
    bbox=[-120.9519, 37.2455, -113.4812, 45.1025],
    collections=["sentinel-s2-l2a-cogs"],
    datetime="2019-08-01/2019-08-03"
).get_all_items()


# Plot the items on an interactive map
stacmap.explore(items)
```

You can color-code items by property by passing a `prop`:

```python
stacmap.explore(items, prop="eo:cloud_cover")
```

Include thumbnail overlays with `thumbnails=True`:

```python
stacmap.explore(items, thumbnails=True)
```

Draw the search bounding box with `bbox`:
```python
stacmap.explore(items, bbox=[-120.9519, 37.2455, -113.4812, 45.1025])
```