# Data Ingestion & Preprocessing

## Responsibility

This module is responsible for acquiring Sentinel-2 L2A imagery
from Copernicus Data Space and preparing it for downstream
super-resolution model processing.

## Pipeline

Copernicus Data Space
        ↓
Authentication
        ↓
Catalog Search
        ↓
Cloud Filtering
        ↓
Scene Selection
        ↓
B02 / B03 / B04 / B08 Download
        ↓
GeoTIFF Validation
        ↓
Band Reading
        ↓
Reflectance Validation
        ↓
Spatial Tiling
        ↓
LR / HR Pair Generation
        ↓
SentinelDataset
        ↓
Model Handoff

## Sentinel-2 Data

Collection:

sentinel-2-l2a

Bands:

- B02 — Blue
- B03 — Green
- B04 — Red
- B08 — Near Infrared

Band ordering:

B02, B03, B04, B08

Data type:

float32

Reflectance range:

0–1

## Raster Representation

Input raster:

(bands, height, width)

Example:

(4, 512, 512)

## Spatial Tiling

Default HR tile:

(4, 64, 64)

The current implementation uses non-overlapping spatial tiles.

For a 512 × 512 input:

512 / 64 = 8 tiles per dimension

8 × 8 = 64 tiles

## LR / HR Prototype

Scale factor:

4

HR:

(4, 64, 64)

LR:

(4, 16, 16)

The current LR data is produced through controlled spatial
downsampling of the input reference raster.

Important:

The generated HR sample is a reference for the current
pipeline prototype. It is not an independently acquired
higher-resolution ground-truth image.

## Dataset Interface

The downstream model receives samples through:

SentinelDataset

Each sample contains:

sample["lr"]
sample["hr"]

Expected shapes:

LR → (4, 16, 16)
HR → (4, 64, 64)

Both are returned as float32 NumPy arrays.

## Validation

The preprocessing layer validates:

- Raster existence
- Raster dimensions
- Band count
- Numeric data type
- NaN / infinite values
- Reflectance range
- Tile dimensions
- LR / HR scale consistency

## Testing

The preprocessing implementation is covered by automated pytest
tests.

The complete project test suite should pass before this branch
is merged.

## Handoff

The preprocessing layer intentionally does not implement SEN2SR
or DSen2.

The model layer consumes the prepared dataset through the
SentinelDataset interface.