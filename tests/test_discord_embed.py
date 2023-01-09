import os

from fastapi import Response
from fastapi.testclient import TestClient

from discord_embed import __version__, settings
from discord_embed.main import app

client: TestClient = TestClient(app)
TEST_FILE: str = "tests/test.mp4"


def test_version() -> None:
    """Test version is correct."""
    assert __version__ == "1.0.0"


def test_domain_ends_with_slash() -> None:
    """Test domain ends with a slash."""
    assert not settings.serve_domain.endswith("/")


def test_save_to_disk() -> None:
    """Test save_to_disk() works."""
    # TODO: Implement this test. I need to mock the UploadFile object.


def test_do_things() -> None:
    """Test do_things() works."""
    # TODO: Implement this test. I need to mock the UploadFile object.


def test_main() -> None:
    """Test main() works."""
    data_without_trailing_nl = ""
    response: Response = client.get("/")

    # Check if response is our HTML.
    with open("templates/index.html", encoding="utf8") as our_html:
        data: str = our_html.read()

        # index.html has a trailing newline that we need to remove.
        if data[-1:] == "\n":
            data_without_trailing_nl: str = data[:-1]  # type: ignore

    assert response.status_code == 200
    assert response.text == data_without_trailing_nl


def test_upload_file() -> None:
    """Test if we can upload files."""
    domain = os.environ["SERVE_DOMAIN"]

    # Remove trailing slash from domain
    if domain.endswith("/"):
        domain: str = domain[:-1]  # type: ignore

    # Upload our video file and check if it returns the html_url.
    with open(TEST_FILE, "rb") as uploaded_file:
        response: Response = client.post(
            url="/uploadfiles/",
            files={"file": uploaded_file},
        )
        returned_json = response.json()
        html_url: str = returned_json["html_url"]

    assert response.status_code == 200
    assert html_url == f"{domain}/test.mp4"
