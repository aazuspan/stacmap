import branca  # type: ignore
import numpy as np
from numpy.typing import NDArray


def get_cmap(cmap: str, n: int) -> NDArray[np.unicode_]:
    """Take a colormap name and return an n-length list of colors. matplotlib will
    be used to parse color names if available. Otherwise, branca will be used.

    Parameters
    ----------
    cmap : str
        The name of the colormap to retrieve.
    n : int
        The number of colors to retrieve.

    Returns
    -------
    list
        A list of hex colors.
    """
    try:
        import matplotlib  # type: ignore
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
            f"Unrecognized cmap: `{cmap}`. Installing matplotlib with `pip install matplotlib` may"
            " resolve this error."
        ) from None
