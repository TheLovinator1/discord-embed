"""Things that has to do with video file uploading."""
import os
from pathlib import Path
from typing import Dict

from fastapi import UploadFile

from discord_embed import settings
from discord_embed.generate_html import generate_html_for_videos
from discord_embed.video import make_thumbnail, video_resolution
from discord_embed.webhook import send_webhook


def save_to_disk(file: UploadFile) -> tuple[str, str]:
    """Save file to disk.

    If spaces in filename, replace with dots.

    Args:
        file (UploadFile): Our file object.

    Returns:
        tuple[str, str]: Returns filename and file location.
    """
    # Create folder if it doesn't exist.
    folder_video = os.path.join(settings.upload_folder, "video")
    Path(folder_video).mkdir(parents=True, exist_ok=True)

    # Replace spaces with dots in filename.
    filename = file.filename.replace(" ", ".")

    # Save file to disk.
    file_location = os.path.join(folder_video, filename)
    with open(file_location, "wb+") as f:
        f.write(file.file.read())

    return filename, file_location


async def do_things(file: UploadFile) -> Dict[str, str]:
    """Save video to disk, generate HTML, thumbnail, and return a .html URL.

    Args:
        file (UploadFile): Our file object.

    Returns:
        Dict[str, str]: Returns URL for video.
    """
    filename, file_location = save_to_disk(file)

    file_url = f"{settings.domain}/video/{filename}"
    height, width = video_resolution(file_location)
    screenshot_url = make_thumbnail(file_location, filename)
    html_url = generate_html_for_videos(
        url=file_url,
        width=width,
        height=height,
        screenshot=screenshot_url,
        filename=filename,
    )
    send_webhook(f"{settings.domain}/{filename} was uploaded.")
    return {"html_url": f"{html_url}"}
