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
        best_scene = client.select_best_scene(scenes)

    best_properties = best_scene.get("properties", {})

    print()
    print("=" * 50)
    print("SELECTED SCENE")
    print("=" * 50)
    print("ID:", best_scene.get("id"))
    print(
        "Date:",
        best_properties.get("datetime"),
    )
    print(
        "Cloud cover:",
        best_properties.get("eo:cloud_cover"),
    )
    scene_datetime = client.get_scene_datetime(best_scene)

    print()
    print("Acquisition datetime:", scene_datetime)


if __name__ == "__main__":
    main()