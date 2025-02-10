from __future__ import annotations

import datetime
import logging
from pathlib import Path
from urllib.parse import urljoin

from discord_embed import settings

logger: logging.Logger = logging.getLogger("uvicorn.error")


def generate_html_for_videos(
    url: str,
    width: int,
    height: int,
    screenshot: str,
    filename: str,
) -> str:
    """Generate HTML for video files.

    Args:
        url: URL for the video. This is accessible from the browser.
        width: This is the width of the video.
        height: This is the height of the video.
        screenshot: URL for the screenshot.
        filename: Original video filename.

    Returns:
        Returns HTML for video.
    """
    time_now: datetime.datetime = datetime.datetime.now(tz=datetime.UTC)
    time_now_str: str = time_now.strftime("%Y-%m-%d %H:%M:%S %Z")

    video_html: str = f"""
    <!DOCTYPE html>
    <html>
    <!-- Generated at {time_now_str} -->
    <head>
        <meta property="og:type" content="video.other">
        <meta property="twitter:player" content="{url}">
        <meta property="og:video:type" content="text/html">
        <meta property="og:video:width" content="{width}">
        <meta property="og:video:height" content="{height}">
        <meta name="twitter:image" content="{screenshot}">
        <meta http-equiv="refresh" content="0;url={url}">
    </head>
    </html>
    """
    domain: str = settings.serve_domain
    html_url: str = urljoin(domain, filename)

    # Take the filename and append .html to it.
    filename += ".html"

    file_path = Path(settings.upload_folder, filename)
    with Path.open(file_path, "w", encoding="utf-8") as f:
        f.write(video_html)

    logger.info("Generated HTML file: %s", html_url)
    logger.info("Saved HTML file to disk: %s", file_path)
    logger.info("Screenshot URL: %s", screenshot)
    logger.info("Video URL: %s", url)
    logger.info("Video resolution: %dx%d", width, height)
    logger.info("Filename: %s", filename)
    logger.info("Domain: %s", domain)
    logger.info("HTML URL: %s", html_url)
    logger.info("Time now: %s", time_now_str)

    return html_url
