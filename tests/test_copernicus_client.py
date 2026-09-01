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