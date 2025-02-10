from __future__ import annotations

import os
from pathlib import Path

from discord_embed import settings
from discord_embed.video import Resolution, make_thumbnail, video_resolution

TEST_FILE = "tests/test.mp4"


def test_video_resolution() -> None:
    """Test video_resolution() works."""
    assert video_resolution(TEST_FILE) == Resolution(height=422, width=422)


def test_make_thumbnail() -> None:
    """Test make_thumbnail() works."""
    domain: str = os.environ["SERVE_DOMAIN"]

    # Remove trailing slash from domain
    if domain.endswith("/"):
        domain: str = domain[:-1]

    # Remove thumbnail if it exists
    thumbnail_path = Path(f"{settings.upload_folder}/test.mp4.jpg")
    if thumbnail_path.exists():
        thumbnail_path.unlink()

    thumbnail: str = make_thumbnail(TEST_FILE, "test.mp4")

    # Check if it returns the correct URL.
    assert thumbnail == f"{domain}/test.mp4.jpg"
