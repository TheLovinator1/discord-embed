import imghdr
import os

from discord_embed import __version__, settings
from discord_embed.generate_html import generate_html_for_videos
from discord_embed.main import app
from discord_embed.video import make_thumbnail, video_resolution
from discord_embed.webhook import send_webhook
from fastapi.testclient import TestClient

client = TestClient(app)
TEST_FILE = "tests/test.mp4"


def test_version():
    """Test that version is correct."""
    assert __version__ == "1.0.0"


def test_domain_ends_with_slash():
    """Test that domain ends with slash."""
    assert not settings.serve_domain.endswith("/")


def test_generate_html_for_videos():
    """Test that generate_html_for_videos() works."""
    # TODO: We should probably import this from settings.py instead of
    # hardcoding it here. If we change it in settings.py, it won't be
    # changed here.

    domain = os.environ["SERVE_DOMAIN"]

    # Remove trailing slash from domain
    if domain.endswith("/"):
        domain = domain[:-1]

    generated_html = generate_html_for_videos(
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        width=1920,
        height=1080,
        screenshot="https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
        filename="test_video.mp4",
    )
    assert generated_html == f"{domain}/test_video.mp4"


def test_video_resolution():
    """Test that video_resolution() works."""
    assert video_resolution(TEST_FILE) == (422, 422)


def test_make_thumbnail():
    """Test that make_thumbnail() works."""
    # TODO: We should probably import this from settings.py instead of
    # hardcoding it here. If we change it in settings.py, it won't be
    # changed here.

    domain = os.environ["SERVE_DOMAIN"]

    # Remove trailing slash from domain
    if domain.endswith("/"):
        domain = domain[:-1]

    thumbnail = make_thumbnail(TEST_FILE, "test.mp4")
    # Check that thumbnail is a jpeg.
    assert imghdr.what(f"{settings.upload_folder}/test.mp4.jpg") == "jpeg"

    # Check that the it returns the correct URL.
    assert thumbnail == f"{domain}/test.mp4.jpg"


def test_save_to_disk():
    """Test that save_to_disk() works."""
    # TODO: Implement this test. I need to mock the UploadFile object.


def test_do_things():
    """Test that do_things() works."""
    # TODO: Implement this test. I need to mock the UploadFile object.


def test_send_webhook():
    """Test that send_webhook() works."""
    send_webhook("Running Pytest")


def test_main():
    """Test that main() works."""
    data_without_trailing_nl = ""
    response = client.get("/")

    # Check if response is our HTML.
    with open("templates/index.html", encoding="utf8") as our_html:
        data = our_html.read()

        # index.html has a trailing newline that we need to remove.
        if data[-1:] == "\n":
            data_without_trailing_nl = data[:-1]

    assert response.status_code == 200
    assert response.text == data_without_trailing_nl


def test_upload_file():
    """Test if we can upload files."""
    # TODO: We should probably import this from settings.py instead of
    # hardcoding it here. If we change it in settings.py, it won't be
    # changed here.

    domain = os.environ["SERVE_DOMAIN"]

    # Remove trailing slash from domain
    if domain.endswith("/"):
        domain = domain[:-1]

    # Upload our video file and check if it returns the html_url.
    with open(TEST_FILE, "rb") as uploaded_file:
        response = client.post(
            url="/uploadfiles/",
            files={"file": uploaded_file},
        )
        returned_json = response.json()
        html_url = returned_json["html_url"]

    assert response.status_code == 200
    assert html_url == f"{domain}/test.mp4"
