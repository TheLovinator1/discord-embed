import imghdr
import os

from discord_embed import settings
from discord_embed.main import (
    app,
    generate_html_for_videos,
    make_thumbnail,
    send_webhook,
    video_resolution,
)
from fastapi.testclient import TestClient

client = TestClient(app)
TEST_FILE = "tests/test.mp4"


def test_domain_ends_with_slash():
    assert not settings.serve_domain.endswith("/")


def test_generate_html_for_videos():
    domain = os.environ["SERVE_DOMAIN"]
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
    resolution = video_resolution(TEST_FILE)
    assert resolution.width == 422
    assert resolution.height == 422


def test_make_thumbnail():
    domain = os.environ["SERVE_DOMAIN"]
    if domain.endswith("/"):
        domain = domain[:-1]

    thumbnail = make_thumbnail(TEST_FILE, "test.mp4")
    assert imghdr.what(f"{settings.upload_folder}/test.mp4.jpg") == "jpeg"
    assert thumbnail == f"{domain}/test.mp4.jpg"


def test_send_webhook():
    send_webhook("Running Pytest")


def test_main():
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
    domain = os.environ["SERVE_DOMAIN"]
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
