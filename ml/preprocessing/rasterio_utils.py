from pathlib import Path
import numpy as np
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
    
def read_bands(
    raster_path: str | Path,
    expected_bands: int = EXPECTED_BANDS,
) -> np.ndarray:
    """
    Read Sentinel-2 bands as a NumPy array.

    Returns:
        Array with shape (bands, height, width)
        and dtype float32.
    """

    metadata = validate_raster(
        raster_path,
        expected_bands=expected_bands,
    )

    with rasterio.open(metadata["path"]) as src:
        data = src.read()

    if not np.isfinite(data).all():
        raise ValueError(
            "Raster contains NaN or infinite values."
        )

    return data.astype(
        np.float32,
        copy=False,
    )
def read_bands(
    raster_path: str | Path,
    expected_bands: int = EXPECTED_BANDS,
) -> np.ndarray:
    """Read and validate Sentinel-2 bands."""

    metadata = validate_raster(
        raster_path,
        expected_bands=expected_bands,
    )

    with rasterio.open(metadata["path"]) as src:
        data = src.read()

    return validate_reflectance(data)

def validate_reflectance(
    data: np.ndarray,
) -> np.ndarray:
    """
    Validate Sentinel-2 reflectance data.

    Expected input shape:
        (4, height, width)

    The four bands are ordered:
        B02, B03, B04, B08
    """

    if data.ndim != 3:
        raise ValueError(
            "Expected raster data with shape (bands, height, width)."
        )

    if data.shape[0] != EXPECTED_BANDS:
        raise ValueError(
            f"Expected {EXPECTED_BANDS} bands, "
            f"but found {data.shape[0]}."
        )

    if not np.isfinite(data).all():
        raise ValueError(
            "Reflectance data contains NaN or infinite values."
        )

    if np.any(data < 0.0) or np.any(data > 1.0):
        raise ValueError(
            "Reflectance values must be between 0 and 1."
        )

    return data.astype(np.float32, copy=False)