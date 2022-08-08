import imghdr
import os

from discord_embed import settings
from discord_embed.video import Resolution, make_thumbnail, video_resolution

TEST_FILE = "tests/test.mp4"


def test_video_resolution():
    """Test video_resolution() works."""
    assert video_resolution(TEST_FILE) == Resolution(height=422, width=422)


def test_make_thumbnail():
    """Test make_thumbnail() works."""
    domain = os.environ["SERVE_DOMAIN"]

    # Remove trailing slash from domain
    if domain.endswith("/"):
        domain = domain[:-1]

    # Remove thumbnail if it exists
    if os.path.exists(f"{settings.upload_folder}/test.mp4.jpg"):
        os.remove(f"{settings.upload_folder}/test.mp4.jpg")

    thumbnail = make_thumbnail(TEST_FILE, "test.mp4")

    # Check if thumbnail is a jpeg.
    assert imghdr.what(f"{settings.upload_folder}/test.mp4.jpg") == "jpeg"

    # Check if it returns the correct URL.
    assert thumbnail == f"{domain}/test.mp4.jpg"
