import os

import pystac

TEST_CATALOG = pystac.Catalog.from_file(
    os.path.join(
        "tests",
        "data",
        "planet-example-v1.0.0-beta.2",
        "hurricane-harvey",
        "catalog.json",
    )
)
TEST_ITEM_COLLECTION = pystac.ItemCollection(TEST_CATALOG.get_all_items())
TEST_ITEM = TEST_ITEM_COLLECTION[0]
