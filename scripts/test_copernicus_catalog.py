import os

import requests
from dotenv import load_dotenv


load_dotenv()


TOKEN_URL = os.getenv("COPERNICUS_TOKEN_URL")
CLIENT_ID = os.getenv("COPERNICUS_CLIENT_ID")
CLIENT_SECRET = os.getenv("COPERNICUS_CLIENT_SECRET")
CATALOG_URL = (
    os.getenv("COPERNICUS_BASE_URL")
    + "/catalog/v1/search"
)
MAX_CLOUD_COVER = 20.0

def get_access_token() -> str:
    """Get an OAuth access token from CDSE."""

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


def search_sentinel2(token: str) -> list[dict]:
    """Search for Sentinel-2 L2A scenes around Chennai."""

    bbox = [80.20, 13.00, 80.30, 13.10]

    payload = {
        "collections": ["sentinel-2-l2a"],
        "bbox": bbox,
        "datetime": (
            "2026-01-01T00:00:00Z/"
            "2026-08-31T23:59:59Z"
        ),
        "limit": 5,
        "filter": f"eo:cloud_cover <= {MAX_CLOUD_COVER}",
    }
    response = requests.post(
        CATALOG_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=60,
    )

    response.raise_for_status()

    return response.json().get("features", [])


def main() -> None:
    token = get_access_token()

    scenes = search_sentinel2(token)

    print(f"Scenes found: {len(scenes)}")

    for index, scene in enumerate(scenes, start=1):
        properties = scene.get("properties", {})

        print()
        print(f"Scene {index}")
        print("-" * 40)
        print("ID:", scene.get("id"))
        print("Date:", properties.get("datetime"))
        print("Cloud cover:", properties.get("eo:cloud_cover"))


if __name__ == "__main__":
    main()