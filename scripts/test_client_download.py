from pathlib import Path

import rasterio

from backend.app.services.copernicus_client import CopernicusClient


OUTPUT_PATH = Path("data/raw/client_test.tif")


def main() -> None:
    client = CopernicusClient()

    scenes = client.search_scenes(
        bbox=[80.20, 13.00, 80.30, 13.10],
        start_datetime="2026-01-01T00:00:00Z",
        end_datetime="2026-08-31T23:59:59Z",
        max_cloud_cover=20.0,
        limit=5,
    )

    scene = client.select_best_scene(scenes)

    output = client.download_bands(
        scene=scene,
        bbox=[80.20, 13.00, 80.30, 13.10],
        output_path=str(OUTPUT_PATH),
        width=512,
        height=512,
        max_cloud_cover=20.0,
    )

    print("Download successful")
    print("Output:", output)

    with rasterio.open(output) as src:
        print("Width:", src.width)
        print("Height:", src.height)
        print("Bands:", src.count)
        print("CRS:", src.crs)
        print("Dtypes:", src.dtypes)


if __name__ == "__main__":
    main()