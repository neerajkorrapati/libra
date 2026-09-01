# Team Libra - SRM Project

## Data Ingestion & Preprocessing
### Owner: Shrivardhini · Branch: `feature/data-ingestion-preprocessing`

## Status

**Completed — Data Ingestion & Preprocessing pipeline**, implemented on the `feature/data-ingestion-preprocessing` branch. Covers Phases 0–5 of the module plan (environment setup, ingestion, preprocessing core, tiling, output handoff contract, testing).

---

## What This Module Does

This module is responsible for everything between "raw Sentinel-2 imagery exists on Copernicus" and "a clean, validated, model-ready tile lands in `data/preprocessed/`." It fetches Sentinel-2 L2A imagery for a given area of interest, filters unusable (cloudy) scenes, validates the raster data, tiles it into fixed-size patches, and generates LR/HR pairs for the super-resolution model to consume downstream.

**Region scope:** Development and testing are currently confined to **Tamil Nadu** (see `docs/data_and_preprocessing.md` for the exact bounding box and sample AOIs used).

---

## Pipeline Overview

```
Copernicus Data Space
   → Authentication
   → Sentinel-2 Catalog Search
   → Cloud Filtering
   → Scene Selection
   → Band Download
   → Raster Validation
   → Band Reading
   → Reflectance Validation
   → Spatial Tiling
   → LR/HR Pair Generation
   → SentinelDataset
   → Model Handoff
```

---

## Module Breakdown

### 1. Copernicus Data Space Integration

A `CopernicusClient` handles all communication with the Copernicus Data Space Ecosystem (CDSE).

**Features:**
- OAuth client-credentials authentication and access-token handling
- Sentinel-2 L2A catalog search (bounding-box based)
- Temporal filtering (date-range queries — see "Handling Sentinel-2's Dynamic Nature" below)
- Cloud-cover filtering and scene selection
- Sentinel-2 data download via the Process API

### 2. Sentinel-2 Bands

| Band | Description |
|------|-------------|
| B02 | Blue |
| B03 | Green |
| B04 | Red |
| B08 | Near Infrared |

Band ordering is fixed as `B02, B03, B04, B08` throughout the pipeline. Downloaded data is stored as `float32` reflectance.

### 3. Raster Validation

Implemented using Rasterio. Validates:
- File existence and validity
- Expected band count
- Raster dimensions
- Numeric data validation
- CRS and raster metadata

### 4. Reflectance Validation

Confirms, before any tile proceeds further:
- The raster contains four bands
- Data is finite (no NaN, no infinite values)
- Reflectance values fall within the expected `0–1` range

### 5. Spatial Tiling

Non-overlapping spatial tile extraction.

**Default configuration:**
- Input raster: `4 × H × W`
- HR tile size: `4 × 64 × 64`

For a `512 × 512` input raster: `512 / 64 = 8` tiles per dimension → `8 × 8 = 64` tiles total.

### 6. LR/HR Pair Generation

Controlled LR/HR pair generation for model training/testing.

**Current prototype configuration:**
- Scale factor: `4`
- HR: `4 × 64 × 64`
- LR: `4 × 16 × 16` (via controlled spatial downsampling of the reference raster)

> **Important caveat, stated plainly for the team and for review:** the current HR sample is a **reference generated from the available Sentinel-2 imagery itself** (via downsampling), **not an independently acquired higher-resolution ground-truth image**. This is a reasonable prototype approach for early development, but it is not the same as validating against true independent high-resolution reference data (e.g., SPOT/NAIP via `opensr-test`, which the validation module owner handles separately). Be prepared to explain this distinction if asked in review — see the "Known Limitations" section.

### 7. Dataset Interface

`SentinelDataset` provides a clean interface for downstream model components:

```python
dataset = SentinelDataset(pairs)
sample = dataset[0]
lr = sample["lr"]
hr = sample["hr"]
```

---

### Configure Copernicus credentials
Copy the example environment file and fill in your own credentials — **never commit real credentials**:
```bash
cp .env.example .env
```
Edit `.env`:
```
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here
```

## Data Contract (What Downstream Modules Can Expect)

- **Output location:** `data/preprocessed/`
- **Format:** `float32` reflectance arrays, band order `B02, B03, B04, B08`, value range `0–1`
- **HR tile shape:** `4 × 64 × 64`
- **LR tile shape:** `4 × 16 × 16` (scale factor 4)
- **Metadata:** each tile is paired with a `.json` sidecar containing geotransform/offset and acquisition date

---
