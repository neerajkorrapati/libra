import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from ml.preprocessing.rasterio_utils import validate_raster


def create_test_raster(
    path,
    bands=4,
    width=32,
    height=32,
):
    """Create a small synthetic GeoTIFF for testing."""

    data = np.ones(
        (bands, height, width),
        dtype=np.float32,
    )

    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=width,
        height=height,
        count=bands,
        dtype="float32",
        crs="EPSG:4326",
        transform=from_origin(
            80.0,
            14.0,
            0.01,
            0.01,
        ),
    ) as dst:
        dst.write(data)


def test_validate_raster(tmp_path):
    """A valid four-band raster should pass validation."""

    raster_path = tmp_path / "test.tif"

    create_test_raster(raster_path)

    metadata = validate_raster(raster_path)

    assert metadata["width"] == 32
    assert metadata["height"] == 32
    assert metadata["count"] == 4
    
def test_validate_raster_rejects_wrong_band_count(tmp_path):
    """A raster with the wrong number of bands should fail."""

    raster_path = tmp_path / "wrong_bands.tif"

    create_test_raster(
        raster_path,
        bands=3,
    )

    with pytest.raises(
        ValueError,
        match="Expected 4 bands",
    ):
        validate_raster(raster_path)


def test_validate_raster_rejects_missing_file(tmp_path):
    """A missing raster should raise FileNotFoundError."""

    raster_path = tmp_path / "does_not_exist.tif"

    with pytest.raises(FileNotFoundError):
        validate_raster(raster_path)