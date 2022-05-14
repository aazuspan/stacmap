stacmap
=======

Explore `STAC <https://stacspec.org/>`_ items and collections on an interactive `Folium <https://python-visualization.github.io/folium/>`_ map with lightweight, minimal dependencies.

.. code-block:: bash

   $ pip install stacmap

To get started, just pass a STAC item or collection to the ``stacmap.explore`` function.

.. code-block:: python

   import stacmap
   from pystac_client import Client

   catalog = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")

   items = catalog.search(
      collections=["landsat-8-c2-l2"],
      bbox=[-112.206, 39.252, -107.988, 42.410],
      datetime="2019-06-01/2019-06-10"
   ).get_all_items()

   stacmap.explore(
      items, prop="eo:cloud_cover", cmap="BuPu",
      style_kwds={"fillOpacity": 0.8}, tiles="CartoDB positron",
      fields=["eo:cloud_cover", "landsat:scene_id", "view:sun_elevation"] 
   )

.. raw:: html

   <iframe src="_static/example_map.html" height="500px" width="100%"></iframe>


.. toctree::
   :maxdepth: 1
   :caption: Contents:

   examples
   api_reference


Indices and tables
==================

* :ref:`genindex`
