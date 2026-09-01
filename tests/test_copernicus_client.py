import os

import pytest

from backend.app.services.copernicus_client import CopernicusClient


def test_client_requires_configuration(monkeypatch):
    """Client should reject missing Copernicus configuration."""

    monkeypatch.delenv("COPERNICUS_CLIENT_ID", raising=False)
    monkeypatch.delenv("COPERNICUS_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("COPERNICUS_TOKEN_URL", raising=False)
    monkeypatch.delenv("COPERNICUS_BASE_URL", raising=False)

    with pytest.raises(RuntimeError, match="Missing required"):
        CopernicusClient()
def test_select_best_scene():
    """Newest acquisition should be selected."""

    client = object.__new__(CopernicusClient)

    scenes = [
        {
            "id": "older-scene",
            "properties": {
                "datetime": "2026-06-28T05:15:10Z",
                "eo:cloud_cover": 15.22,
            },
        },
        {
            "id": "newer-scene",
            "properties": {
                "datetime": "2026-07-15T05:15:29Z",
                "eo:cloud_cover": 0.83,
            },
        },
        {
            "id": "oldest-scene",
            "properties": {
                "datetime": "2026-06-05T05:15:28Z",
                "eo:cloud_cover": 5.58,
            },
        },
    ]

    selected = client.select_best_scene(scenes)

    assert selected["id"] == "newer-scene"
def test_select_best_scene_raises_when_empty():
    """Selection should fail clearly when no scenes exist."""

    client = object.__new__(CopernicusClient)

    with pytest.raises(
        ValueError,
        match="No suitable Sentinel-2 scenes",
    ):
        client.select_best_scene([])