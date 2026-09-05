import os

import requests
from dotenv import load_dotenv


load_dotenv()


CLIENT_ID = os.getenv("COPERNICUS_CLIENT_ID")
CLIENT_SECRET = os.getenv("COPERNICUS_CLIENT_SECRET")
TOKEN_URL = os.getenv("COPERNICUS_TOKEN_URL")


def main() -> None:
    if not CLIENT_ID:
        raise RuntimeError(
            "COPERNICUS_CLIENT_ID is missing from .env"
        )

    if not CLIENT_SECRET:
        raise RuntimeError(
            "COPERNICUS_CLIENT_SECRET is missing from .env"
        )

    if not TOKEN_URL:
        raise RuntimeError(
            "COPERNICUS_TOKEN_URL is missing from .env"
        )

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

    token_data = response.json()

    if "access_token" not in token_data:
        raise RuntimeError(
            "Copernicus did not return an access token."
        )

    print("Copernicus authentication: SUCCESS")
    print("Token type:", token_data.get("token_type"))
    print("Expires in:", token_data.get("expires_in"), "seconds")


if __name__ == "__main__":
    main()