"""Stuff that has to do with videos."""
import sys

import ffmpeg

from discord_embed import settings


def video_resolution(path_to_video: str) -> tuple[int, int]:
    """Find video resolution.

    Args:
        path_to_video: Path to video file.

    Returns:
        Returns height and width.
    """
    probe = ffmpeg.probe(path_to_video)
    video_stream = next((stream for stream in probe["streams"] if stream["codec_type"] == "video"), None)
    if video_stream is None:
        print("No video stream found", file=sys.stderr)
        sys.exit(1)

    width = int(video_stream["width"])
    height = int(video_stream["height"])

    return height, width


def make_thumbnail(path_video: str, file_filename: str) -> str:
    """Make thumbnail for Discord. This is a screenshot of the video.

    Args:
        path_video: Path where video file is stored.
        file_filename: File name for URL.

    Returns:
        Returns thumbnail filename.
    """
    (
        ffmpeg.input(path_video, ss="1")
        .output(f"{settings.upload_folder}/{file_filename}.jpg", vframes=1)
        .overwrite_output()
        .run()
    )
    # Return URL for thumbnail.
    return f"{settings.serve_domain}/{file_filename}.jpg"
