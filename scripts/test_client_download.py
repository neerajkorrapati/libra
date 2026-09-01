from pathlib import Path

import rasterio

from backend.app.services.copernicus_client import CopernicusClient


OUTPUT_PATH = Path("data/raw/client_test.tif")


def main() -> None:
    client = CopernicusClient()

    output = client.download_bands(
        bbox=[80.20, 13.00, 80.30, 13.10],
        start_datetime="2026-07-15T00:00:00Z",
        end_datetime="2026-07-16T00:00:00Z",
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