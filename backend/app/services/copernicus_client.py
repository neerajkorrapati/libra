import os

import requests
from dotenv import load_dotenv


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