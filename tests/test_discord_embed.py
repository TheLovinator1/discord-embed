from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from fastapi.testclient import TestClient

from discord_embed.main import app, serve_domain

if TYPE_CHECKING:
    import httpx

client: TestClient = TestClient(app)
TEST_FILE: str = "tests/test.mp4"


def test_domain_ends_with_slash() -> None:
    """Test domain ends with a slash."""
    assert not serve_domain.endswith("/")


def test_main() -> None:
    """Test main() works."""
    response: httpx.Response = client.get("/")
    assert response.is_success


def test_upload_file() -> None:
    """Test if we can upload files."""
    domain = os.environ["SERVE_DOMAIN"].removesuffix("/")

    # Upload our video file and check if it returns the html_url.
    with Path.open(Path(TEST_FILE), "rb") as uploaded_file:
        response: httpx.Response = client.post(
            url="/uploadfiles/",
            files={"file": uploaded_file},
        )
        returned_json = response.json()
        html_url: str = returned_json["html_url"]

    assert response.is_success
    assert html_url == f"{domain}/test.mp4"
