# stacmap

[![PyPI version](https://badge.fury.io/py/stacmap.svg)](https://badge.fury.io/py/stacmap)
[![Documentation Status](https://readthedocs.org/projects/pip/badge/?version=latest)](https://stacmap.readthedocs.io/en/latest/)
[![nbviewer](https://raw.githubusercontent.com/jupyter/design/master/logos/Badges/nbviewer_badge.svg)](https://nbviewer.org/github/aazuspan/stacmap/blob/main/docs/source/tutorials/quickstart.ipynb)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/aazuspan/stacmap/HEAD?labpath=docs%2Fsource%2Ftutorials%2Fquickstart.ipynb)

Create interactive maps of [STAC](https://stacspec.org/) items and collections without the heavy dependencies and boilerplate of `geopandas.GeoDataFrame.explore`.

# Features

- 🗺️ Explore STAC item footprints
- 🌈 Color-code items by properties
- 🖼️ Preview item thumbnails
- 🪶 Lightweight dependencies (just `folium` and `pystac`)

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
    collections=["landsat-c2l2-srby"],
    datetime="2019-08-01/2019-08-03"
).get_all_items()


# Plot the items on an interactive map, color-coded by cloud cover
stacmap.explore(items, prop="eo:cloud_cover")
```

Check out [the docs](https://stacmap.readthedocs.io/en/latest/) for details or try out an [interactive notebook](https://mybinder.org/v2/gh/aazuspan/stacmap/HEAD?labpath=docs%2Fsource%2Ftutorials%2Fquickstart.ipynb) in Binder.

# Compared to geopandas

Let's look at a simple example to see how `stacmap` simplifies plotting a STAC collection and search bounds over `geopandas`.

First, we'll load our STAC items:

```python
from pystac_client import Client

catalog = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")

bbox = (-67.008753, -9.96445, -65.615556, -8.57408)

items = catalog.search(
    collections=["sentinel-2-l2a"],
    bbox=bbox,
    datetime="2019-06-01/2019-06-10"
).get_all_items()
```

Now we'll create an interactive map that shows our items and our bounding box.

<table>

<tr>
<th> geopandas </th>
<th> stacmap </th>
</tr>

<tr>
<td>
  
``` python
!pip install geopandas folium mapclassify matplotlib

import geopandas as gpd
import shapely
import folium

gdf = gpd.GeoDataFrame.from_features(
    items.to_dict(), 
    crs="EPSG:4326"
)
bbox_geom = shapely.geometry.mapping(shapely.geometry.box(*bbox))
bbox_layer = folium.GeoJson(bbox_geom)

m = gdf.explore(column="eo:cloud_cover")
bbox_layer.add_to(m)
m
```

</td>
<td>

``` python
!pip install stacmap

import stacmap

stacmap.explore(
    items, 
    prop="eo:cloud_cover", 
    bbox=bbox
)
```
</td>
</tr>

</table>
