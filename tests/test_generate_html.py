from __future__ import annotations

import os
from pathlib import Path

from discord_embed.generate_html import generate_html_for_videos


def test_generate_html_for_videos() -> None:
    """Test generate_html_for_videos() works."""
    domain: str = os.environ["SERVE_DOMAIN"]

    # Remove trailing slash from domain
    if domain.endswith("/"):
        domain = domain[:-1]

    # Delete the old HTML file if it exists
    if Path.exists(Path("Uploads/test_video.mp4.html")):
        Path.unlink(Path("Uploads/test_video.mp4.html"))

    generated_html: str = generate_html_for_videos(
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        width=1920,
        height=1080,
        screenshot="https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
        filename="test_video.mp4",
    )
    assert generated_html == f"{domain}/test_video.mp4"
