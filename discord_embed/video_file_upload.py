from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from discord_embed import settings
from discord_embed.generate_html import generate_html_for_videos
from discord_embed.video import Resolution, make_thumbnail, video_resolution

if TYPE_CHECKING:
    from fastapi import UploadFile


@dataclass
class VideoFile:
    """A video file.

    filename: The filename of the video file.
    location: The location of the video file.
    """

    filename: str
    location: str


def save_to_disk(file: UploadFile) -> VideoFile:
    """Save the uploaded file to disk.

    If spaces in the filename, replace with dots.

    Args:
        file: Our uploaded file.

    Raises:
        ValueError: If the filename is None.

    Returns:
        VideoFile object with the filename and location.
    """
    if file.filename is None:
        msg = "Filename is None"
        raise ValueError(msg)

    # Create the folder where we should save the files
    save_folder_video = Path(settings.upload_folder, "video")
    Path(save_folder_video).mkdir(parents=True, exist_ok=True)

    # Replace spaces with dots in the filename.
    filename: str = file.filename.replace(" ", ".")

    # Save the uploaded file to disk.
    file_location = Path(save_folder_video, filename)
    with Path.open(file_location, "wb+") as f:
        f.write(file.file.read())

    return VideoFile(filename, str(file_location))


def do_things(file: UploadFile) -> str:
    """Save video to disk, generate HTML, thumbnail, and return a .html URL.

    Args:
        file: Our uploaded file.

    Returns:
        Returns URL for video.
    """
    video_file: VideoFile = save_to_disk(file)

    file_url: str = f"{settings.serve_domain}/video/{video_file.filename}"
    res: Resolution = video_resolution(video_file.location)
    screenshot_url: str = make_thumbnail(video_file.location, video_file.filename)
    html_url: str = generate_html_for_videos(
        url=file_url,
        width=res.width,
        height=res.height,
        screenshot=screenshot_url,
        filename=video_file.filename,
    )
    return html_url
