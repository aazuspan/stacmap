import branca
import numpy as np


def get_cmap(cmap: str, n: int):
    """Take a colormap name (or possibly a list of colors or a colormap object?) and return ???. Maybe an n-sized list of hex colors? Need to think about it."""
    try:
        import matplotlib
    except ImportError:
        matplotlib = None

    if matplotlib is not None:
        colors = matplotlib.cm.get_cmap(cmap)(np.linspace(0, 1, n))
        return np.apply_along_axis(matplotlib.colors.to_hex, 1, colors)
    try:
        base_colors = branca.utilities.color_brewer(cmap)
        return branca.utilities.linear_gradient(base_colors, n)
    except ValueError:
        raise ValueError(
            f"Unrecognized cmap: `{cmap}`. Installing matplotlib with `pip install matplotlib` may resolve this error."
        ) from None
