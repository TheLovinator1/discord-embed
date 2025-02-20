from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from discord_embed import settings
from discord_embed.generate_html import generate_html_for_videos
from discord_embed.main import remove_illegal_chars
from discord_embed.video import Resolution, make_thumbnail, video_resolution

if TYPE_CHECKING:
    from fastapi import UploadFile

logger: logging.Logger = logging.getLogger("uvicorn.error")


def do_things(file: UploadFile) -> str:
    """Save video to disk, generate HTML, thumbnail, and return a .html URL.

    Args:
        file: Our uploaded file.

    Raises:
        ValueError: If the filename is None.

    Returns:
        Returns URL for video.
    """
    if file.filename is None:
        msg = "Filename is None"
        raise ValueError(msg)

    # Create the folder where we should save the files
    save_folder_video = Path(settings.upload_folder, "video")
    Path(save_folder_video).mkdir(parents=True, exist_ok=True)

    # Replace spaces with dots and remove illegal characters
    filename: str = file.filename.replace(" ", ".")
    filename = remove_illegal_chars(filename)
    filename = filename.strip()

    # Save the uploaded file to disk.
    file_location = Path(save_folder_video, filename)
    with Path.open(file_location, "wb+") as f:
        f.write(file.file.read())

    file_url: str = f"{settings.serve_domain}/video/{filename}"
    res: Resolution = video_resolution(str(file_location))
    screenshot_url: str = make_thumbnail(str(file_location), filename)
    html_url: str = generate_html_for_videos(
        url=file_url,
        width=res.width,
        height=res.height,
        screenshot=screenshot_url,
        filename=filename,
    )
    logger.info("Generated HTML URL: %s", html_url)
    logger.debug("Video file location: %s", str(file_location))
    logger.debug("Video filename: %s", filename)

    return html_url
