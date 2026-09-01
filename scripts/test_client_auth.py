from backend.app.services.copernicus_client import CopernicusClient


def main() -> None:
    client = CopernicusClient()

    token = client.authenticate()

    print("CopernicusClient authentication: SUCCESS")
    print("Access token received:", bool(token))


if __name__ == "__main__":
    main()