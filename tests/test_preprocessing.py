import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from ml.preprocessing.rasterio_utils import validate_raster

from ml.preprocessing.rasterio_utils import (
    read_bands,
    validate_raster,
    validate_reflectance,
)
from ml.preprocessing.tile_loader import extract_tiles

from ml.datasets.dataset_loader import create_lr_hr_pairs

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

def test_read_bands(tmp_path):
    """Four-band raster should be returned as float32 data."""

    raster_path = tmp_path / "test.tif"

    create_test_raster(
        raster_path,
        bands=4,
        width=32,
        height=32,
    )

    data = read_bands(raster_path)

    assert data.shape == (4, 32, 32)
    assert data.dtype == np.float32
    assert np.isfinite(data).all()

def test_validate_reflectance():
    data = np.ones(
        (4, 16, 16),
        dtype=np.float32,
    ) * 0.25

    result = validate_reflectance(data)

    assert result.shape == (4, 16, 16)
    assert result.dtype == np.float32


def test_validate_reflectance_rejects_out_of_range():
    data = np.ones(
        (4, 16, 16),
        dtype=np.float32,
    )

    data[0, 0, 0] = 1.5

    with pytest.raises(
        ValueError,
        match="between 0 and 1",
    ):
        validate_reflectance(data)

def test_extract_tiles():
    """A 128x128 raster should produce four 64x64 tiles."""

    data = np.zeros(
        (4, 128, 128),
        dtype=np.float32,
    )

    tiles = list(
        extract_tiles(
            data,
            tile_size=64,
        )
    )

    assert len(tiles) == 4

    for tile in tiles:
        assert tile.shape == (4, 64, 64)
        assert tile.dtype == np.float32

def test_extract_tiles_rejects_invalid_dimensions():
    """Tile extraction should reject non-raster input."""

    data = np.zeros(
        (128, 128),
        dtype=np.float32,
    )

    with pytest.raises(
        ValueError,
        match="shape",
    ):
        list(extract_tiles(data))

def test_extract_tiles_rejects_too_large_tile():
    """Tile size cannot exceed raster dimensions."""

    data = np.zeros(
        (4, 32, 32),
        dtype=np.float32,
    )

    with pytest.raises(
        ValueError,
        match="cannot exceed",
    ):
        list(
            extract_tiles(
                data,
                tile_size=64,
            )
        )

def test_create_lr_hr_pairs(tmp_path):
    """Create correctly shaped LR/HR pairs."""

    raster_path = tmp_path / "input.tif"

    create_test_raster(
        raster_path,
        bands=4,
        width=128,
        height=128,
    )

    output_dir = tmp_path / "pairs"

    pairs = create_lr_hr_pairs(
        raster_path,
        output_dir,
        hr_tile_size=64,
        scale=4,
    )

    assert len(pairs) == 4

    hr = np.load(pairs[0]["hr"])
    lr = np.load(pairs[0]["lr"])

    assert hr.shape == (4, 64, 64)
    assert lr.shape == (4, 16, 16)

    assert hr.dtype == np.float32
    assert lr.dtype == np.float32

def test_create_lr_hr_pairs_rejects_invalid_scale(tmp_path):
    """Scale must be greater than one."""

    raster_path = tmp_path / "input.tif"

    create_test_raster(raster_path)

    with pytest.raises(
        ValueError,
        match="greater than 1",
    ):
        create_lr_hr_pairs(
            raster_path,
            tmp_path / "pairs",
            scale=1,
        )

def test_create_lr_hr_pairs_rejects_incompatible_tile_size(
    tmp_path,
):
    """HR tile size must be divisible by scale."""

    raster_path = tmp_path / "input.tif"

    create_test_raster(raster_path)

    with pytest.raises(
        ValueError,
        match="divisible",
    ):
        create_lr_hr_pairs(
            raster_path,
            tmp_path / "pairs",
            hr_tile_size=65,
            scale=4,
        )