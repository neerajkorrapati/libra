import os
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()


TOKEN_URL = os.getenv("COPERNICUS_TOKEN_URL")
CLIENT_ID = os.getenv("COPERNICUS_CLIENT_ID")
CLIENT_SECRET = os.getenv("COPERNICUS_CLIENT_SECRET")

PROCESS_URL = (
    os.getenv("COPERNICUS_BASE_URL")
    + "/api/v1/process"
)


BBOX = [80.20, 13.00, 80.30, 13.10]

OUTPUT_PATH = Path("data/raw/chennai_test.tif")


def get_access_token() -> str:
    """Get an OAuth access token."""

    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        timeout=30,
    )

    response.raise_for_status()

    return response.json()["access_token"]


def download_sentinel2(token: str) -> None:
    """Download four Sentinel-2 bands for the test AOI."""

    evalscript = """
    //VERSION=3

    function setup() {
        return {
            input: [{
                bands: ["B02", "B03", "B04", "B08"],
                units: "REFLECTANCE"
            }],
            output: {
                bands: 4,
                sampleType: "FLOAT32"
            }
        };
    }

    function evaluatePixel(sample) {
        return [
            sample.B02,
            sample.B03,
            sample.B04,
            sample.B08
        ];
    }
    """

    payload = {
        "input": {
            "bounds": {
                "bbox": BBOX
            },
            "data": [
                {
                    "type": "sentinel-2-l2a",
                    "dataFilter": {
                        "timeRange": {
                            "from": "2026-07-15T00:00:00Z",
                            "to": "2026-07-16T00:00:00Z"
                        },
                        "maxCloudCoverage": 20,
                        "mosaickingOrder": "mostRecent"
                    }
                }
            ]
        },
        "output": {
            "width": 512,
            "height": 512,
            "responses": [
                {
                    "identifier": "default",
                    "format": {
                        "type": "image/tiff"
                    }
                }
            ]
        },
        "evalscript": evalscript
    }

    response = requests.post(
        PROCESS_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=300,
    )

    response.raise_for_status()

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_PATH.write_bytes(response.content)

    print("Download successful")
    print("Output:", OUTPUT_PATH)
    print("Size:", len(response.content), "bytes")


def main() -> None:
    token = get_access_token()
    download_sentinel2(token)


if __name__ == "__main__":
    main()