from collections.abc import Iterator

import numpy as np


def extract_tiles(
    data: np.ndarray,
    tile_size: int = 64,
) -> Iterator[np.ndarray]:
    """
    Extract non-overlapping spatial tiles from a raster.

    Args:
        data: Raster array with shape
            (bands, height, width).
        tile_size: Width and height of each tile.

    Yields:
        Tiles with shape:
            (bands, tile_size, tile_size)
    """

    if data.ndim != 3:
        raise ValueError(
            "Expected data with shape (bands, height, width)."
        )

    if tile_size <= 0:
        raise ValueError(
            "tile_size must be greater than zero."
        )

    _, height, width = data.shape

    if height < tile_size or width < tile_size:
        raise ValueError(
            "Tile size cannot exceed raster dimensions."
        )

    for row in range(
        0,
        height - tile_size + 1,
        tile_size,
    ):
        for col in range(
            0,
            width - tile_size + 1,
            tile_size,
        ):
            yield data[
                :,
                row:row + tile_size,
                col:col + tile_size,
            ]