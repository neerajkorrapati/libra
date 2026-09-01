import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

load_dotenv()


class CopernicusClient:
    """Client for interacting with Copernicus Data Space APIs."""

    def __init__(self) -> None:
        self.client_id = os.getenv("COPERNICUS_CLIENT_ID")
        self.client_secret = os.getenv("COPERNICUS_CLIENT_SECRET")
        self.token_url = os.getenv("COPERNICUS_TOKEN_URL")
        self.base_url = os.getenv("COPERNICUS_BASE_URL")

        self._validate_configuration()

        self._access_token: str | None = None

    def _validate_configuration(self) -> None:
        """Validate required Copernicus configuration."""

        required = {
            "COPERNICUS_CLIENT_ID": self.client_id,
            "COPERNICUS_CLIENT_SECRET": self.client_secret,
            "COPERNICUS_TOKEN_URL": self.token_url,
            "COPERNICUS_BASE_URL": self.base_url,
        }

        missing = [
            name
            for name, value in required.items()
            if not value
        ]

        if missing:
            raise RuntimeError(
                "Missing required Copernicus configuration: "
                + ", ".join(missing)
            )

    def authenticate(self) -> str:
        """Authenticate with CDSE and return an access token."""

        response = requests.post(
            self.token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            timeout=30,
        )

        response.raise_for_status()

        token_data = response.json()

        access_token = token_data.get("access_token")

        if not access_token:
            raise RuntimeError(
                "Copernicus authentication response "
                "did not contain an access token."
            )

        self._access_token = access_token

        return access_token
    
    def search_scenes(
        self,
        bbox: list[float],
        start_datetime: str,
        end_datetime: str,
        max_cloud_cover: float = 20.0,
        limit: int = 10,
    ) -> list[dict]:
            """Search for Sentinel-2 L2A scenes matching the criteria."""

            if self._access_token is None:
                self.authenticate()

            catalog_url = f"{self.base_url}/catalog/v1/search"

            payload = {
                "collections": ["sentinel-2-l2a"],
                "bbox": bbox,
                "datetime": f"{start_datetime}/{end_datetime}",
                "limit": limit,
                "filter": (
                    f"eo:cloud_cover <= {max_cloud_cover}"
                ),
            }

            response = requests.post(
                catalog_url,
                headers={
                    "Authorization": (
                        f"Bearer {self._access_token}"
                    ),
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=60,
            )

            response.raise_for_status()

            data = response.json()

            return data.get("features", [])
    def select_best_scene(
        self,
        scenes: list[dict],
    ) -> dict:
        """Select the most recent suitable scene."""

        if not scenes:
            raise ValueError(
                "No suitable Sentinel-2 scenes were found."
            )

        return max(
            scenes,
            key=lambda scene: scene.get(
                "properties", {}
            ).get("datetime", ""),
        )
    def get_scene_datetime(self, scene: dict) -> str:
        """Return the acquisition datetime of a Catalog scene."""

        datetime_value = (
            scene.get("properties", {}).get("datetime")
        )

        if not datetime_value:
            raise ValueError(
                "Selected scene does not contain an acquisition datetime."
            )

        return datetime_value
    
    def download_bands(
        self,
        scene: dict,
        bbox: list[float],
        output_path: str,
        width: int = 512,
        height: int = 512,
        max_cloud_cover: float = 20.0,
    ) -> str:
        """Download Sentinel-2 B02, B03, B04 and B08 as GeoTIFF."""

        if self._access_token is None:
            self.authenticate()

        scene_datetime = self.get_scene_datetime(scene)
        acquisition_time = datetime.fromisoformat(
        scene_datetime.replace("Z", "+00:00")
        )

        start_time = acquisition_time - timedelta(minutes=1)
        end_time = acquisition_time + timedelta(minutes=1)

        process_start = (
            start_time.astimezone(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        )

        process_end = (
            end_time.astimezone(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        )
        process_url = f"{self.base_url}/api/v1/process"

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
                    "bbox": bbox
                },
                "data": [
                    {
                        "type": "sentinel-2-l2a",
                        "dataFilter": {
                            "timeRange": {
                                "from": process_start,
                                "to": process_end,
                            },
                            "maxCloudCoverage": max_cloud_cover,
                            "mosaickingOrder": "mostRecent",
                        },
                    }
                ],
            },
            "output": {
                "width": width,
                "height": height,
                "responses": [
                    {
                        "identifier": "default",
                        "format": {
                            "type": "image/tiff"
                        },
                    }
                ],
            },
            "evalscript": evalscript,
        }

        response = requests.post(
            process_url,
            headers={
                "Authorization": (
                    f"Bearer {self._access_token}"
                ),
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=300,
        )

        response.raise_for_status()

        output = Path(output_path)
        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output.write_bytes(response.content)

        return str(output)