from backend.app.services.copernicus_client import CopernicusClient


def main() -> None:
    client = CopernicusClient()

    scenes = client.search_scenes(
        bbox=[80.20, 13.00, 80.30, 13.10],
        start_datetime="2026-01-01T00:00:00Z",
        end_datetime="2026-08-31T23:59:59Z",
        max_cloud_cover=20.0,
        limit=5,
    )

    print(f"Scenes found: {len(scenes)}")

    for index, scene in enumerate(scenes, start=1):
        properties = scene.get("properties", {})

        print()
        print(f"Scene {index}")
        print("-" * 40)
        print("ID:", scene.get("id"))
        print("Date:", properties.get("datetime"))
        print(
            "Cloud cover:",
            properties.get("eo:cloud_cover"),
        )


if __name__ == "__main__":
    main()