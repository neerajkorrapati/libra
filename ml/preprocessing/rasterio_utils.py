from pathlib import Path

import rasterio


EXPECTED_BANDS = 4


def validate_raster(
    raster_path: str | Path,
    expected_bands: int = EXPECTED_BANDS,
) -> dict:
    """
    Validate a raster and return basic metadata.

    The current ingestion pipeline produces a four-band
    Sentinel-2 GeoTIFF containing B02, B03, B04 and B08.
    """

    path = Path(raster_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Raster file does not exist: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Raster path is not a file: {path}"
        )

    with rasterio.open(path) as src:
        if src.count != expected_bands:
            raise ValueError(
                f"Expected {expected_bands} bands, "
                f"but found {src.count}."
            )

        if src.width <= 0 or src.height <= 0:
            raise ValueError(
                "Raster dimensions must be greater than zero."
            )

        return {
            "path": str(path),
            "width": src.width,
            "height": src.height,
            "count": src.count,
            "crs": src.crs,
            "dtypes": src.dtypes,
            "bounds": src.bounds,
        }