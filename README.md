# TerraSharp — Deep Learning Based Super Resolution Mapping (SRM)
### Smart India Hackathon 2026 · Problem Statement 26142 · Team Libra

> Turning free, frequently-refreshed satellite imagery into sharper, validated, decision-ready insight — without pretending the AI is more certain than it is.

---

## Problem Statement

| | |
|---|---|
| **PS ID** | 26142 |
| **Title** | Deep Learning Based Super Resolution Mapping (SRM) from Medium Resolution Satellite Imageries |
| **Organization** | National Technical Research Organisation (NTRO) |
| **Theme** | Space Technology |
| **Category** | Software |

**The problem, in one line:** Sentinel-2 satellite imagery is free, covers all of India, and refreshes every 5 days — but at 10m resolution, it's too coarse to reliably identify small buildings, narrow roads, field boundaries, or localized damage. Commercial high-resolution imagery solves this but must be specifically tasked, is expensive, and isn't always available on short notice.

---

## What We Built

**TerraSharp** takes real Sentinel-2 L2A imagery (10m resolution) and uses a fine-tuned AI super-resolution model to reconstruct a sharper version (<4m resolution) — while explicitly validating and reporting how much of that enhancement can actually be trusted, rather than just showing a prettier picture.

This is **not** a text-to-image generator and does not invent scenes from prompts. It takes a real, downloaded satellite photograph as input and produces a reconstructed, higher-detail version of that same real photograph as output — grounded in patterns learned from real paired low-resolution/high-resolution training data.

### What makes this different from "just running a sharpening filter"

Most super-resolution demos stop at "look how much sharper this is." We treat that as half the problem. Generative super-resolution models are known in the research literature to sometimes hallucinate plausible-looking detail that isn't actually there — so alongside the enhancement, TerraSharp includes a **dedicated validation and uncertainty layer** that scores accuracy against real high-resolution reference data and produces a confidence map showing which parts of the output are well-supported versus more of an educated guess. We also demonstrate real downstream utility — running a building/road detector on both the original and enhanced imagery to show the enhancement produces genuinely more useful results, not just visually nicer ones.

---

## Pipeline Overview

```
Sentinel-2 (Copernicus)
   → Data Ingestion & Preprocessing   (cloud filtering, band stacking, tiling)
   → AI Super-Resolution              (SEN2SR primary, DSen2 fallback)
   → Validation & Uncertainty Layer   (PSNR / SSIM / spectral consistency + confidence map)
   → Downstream Application           (building/road detection uplift demo)
   → React Frontend                   (AOI selection, before/after, confidence overlay)
```

For the full layered architecture diagram, module responsibilities, and design rationale, see [`docs/architecture.md`](docs/architecture.md).

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + Leaflet |
| Backend/API | FastAPI |
| Primary SR model | SEN2SR (ESA-affiliated, pretrained + fine-tuned) |
| Fallback SR model | DSen2 |
| ML framework | PyTorch |
| Data source | Copernicus Data Space Ecosystem (Sentinel-2 L2A) |
| Geospatial processing | rasterio, GDAL, numpy |
| Validation | opensr-test, scikit-image |
| Downstream detection | Pretrained YOLOv8 (inference only) |
| Compute | Google Colab / Kaggle free-tier GPU |

Full details, locked decisions, and the "do not deviate" list are in [`docs/tech_stack.md`](docs/tech_stack.md) — read this before introducing any new library or swapping a component.

## Region Scope

Development and testing are currently scoped to **Tamil Nadu**, using three representative AOIs chosen to match our use-case narrative:

| AOI | Region | Use case |
|---|---|---|
| Urban/dense settlement | Chennai / Coimbatore outskirts | Informal settlement & urban mapping |
| Agriculture | Cauvery delta, near Thanjavur | Fragmented small-farm crop monitoring |
| Coastal | Near Nagapattinam / Cuddalore | Flood/cyclone disaster-response relevance |

---

## Getting Started

### Prerequisites
- Python 3.10
- Node.js (for the React frontend — see `frontend/README.md` for the exact version)
- GDAL installed at the system level (required by `rasterio`)
- A free Copernicus Data Space Ecosystem account (OAuth client ID + secret)

### Quick Start
```bash
git clone <repo-url>
cd srm-project

# Backend / ML environment
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # fill in Copernicus credentials

# Fetch sample data and run the demo pipeline
python scripts/download_sample_tiles.py
python scripts/run_demo_pipeline.py

# Frontend
cd frontend
npm install
npm start
```

For module-specific setup (fine-tuning the model, running validation benchmarks, etc.), see the individual module READMEs linked above.

### Running Tests
```bash
pytest tests/ -v
```

---

## Why This Matters

- **Cost and speed:** Extracts more analytical value from satellite data India already has free, continuous access to — instead of depending on expensive, specifically-tasked commercial imagery for every use case.
- **Disaster response:** Offers a faster first-look option using already-available imagery when time-critical commercial tasking isn't feasible.
- **Agriculture & urban planning:** Improves the practical usability of Sentinel-2's frequent, full-country coverage for tasks that currently need finer detail than 10m resolution allows.
- **Honesty by design:** The validation/uncertainty layer means outputs come with an explicit statement of confidence — this is a decision-support tool, not an autonomous ground-truth generator.

---

## Known Limitations

- Currently scoped to Tamil Nadu only; generalizing to other regions requires re-validating cloud-cover thresholds and tile assumptions against different land-cover types.
- Independent high-resolution reference data for India is scarce; validation currently supplements internally-derived reference pairs with available SPOT/NAIP-based benchmarks (see `ml/validation/README.md` for specifics).
- Not a real-time system — designed for on-demand or batch analysis of existing/recently captured imagery.
- Multi-temporal fusion (combining several Sentinel-2 revisits of the same area to improve confidence) is identified as a promising future extension, not implemented in this prototype.

---

## Team Libra

| Role | Responsibility |
|---|---|
| Data Ingestion & Preprocessing | Sentinel-2 fetch, cloud filtering, tiling, geospatial consistency |
| AI Model | SEN2SR integration & fine-tuning, DSen2 fallback |
| Validation & Uncertainty | Accuracy metrics, confidence map generation |
| Downstream Application & Backend | Detection uplift demo, FastAPI orchestration |
| Frontend & Demo | React UI, live demo, presentation |

---

## References

See [`docs/literature_review.md`](docs/literature_review.md) for full citations, including SEN2SR, DSen2, and the OpenSR-test validation benchmark this project builds on.