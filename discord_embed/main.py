from __future__ import annotations

import logging
from pathlib import Path
from typing import Annotated
from urllib.parse import urljoin

import sentry_sdk
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse

from discord_embed.settings import serve_domain, upload_folder, webhook_url
from discord_embed.video_file_upload import do_things
from discord_embed.webhook import send_webhook

sentry_sdk.init(
    dsn="https://61f2ac51bc9083592bab1e3794305ec0@o4505228040339456.ingest.us.sentry.io/4508796999434240",
    send_default_pii=True,
    traces_sample_rate=1.0,
    _experiments={"continuous_profiling_auto_start": True},
)

app: FastAPI = FastAPI(
    title="discord-nice-embed",
    contact={
        "name": "Github repo",
        "url": "https://github.com/TheLovinator1/discord-embed",
    },
)
logger: logging.Logger = logging.getLogger("uvicorn.error")

logger.info("Server started on http://localhost:8000/")
logger.debug("\tServe domain: %s", serve_domain)
logger.debug("\tUpload folder: %s", upload_folder)
logger.debug("\tWebhook URL: %s", webhook_url)


@app.post("/uploadfiles/", description="Where to send a POST request to upload files.")
async def upload_file(file: Annotated[UploadFile, File()]) -> JSONResponse:
    """Page for uploading files.

    If it is a video, we need to make an HTML file, and a thumbnail
    otherwise we can just save the file and return the URL for it.
    If something goes wrong, we will send a message to Discord.

    Args:
        file: Our uploaded file.

    Returns:
        Returns a dict with the filename, or a link to the .html if it was a video.
    """
    if file.filename is None:
        send_webhook("Filename is None")
        return JSONResponse(content={"error": "Filename is None"}, status_code=500)
    if file.content_type is None:
        send_webhook("Content type is None")
        return JSONResponse(content={"error": "Content type is None"}, status_code=500)

    if file.content_type.startswith("video/"):
        html_url: str = do_things(file)
    else:
        filename: str = remove_illegal_chars(file.filename)

        with Path.open(Path(upload_folder, filename), "wb+") as f:
            f.write(file.file.read())

        html_url: str = urljoin(serve_domain, filename)

    send_webhook(f"{html_url} was uploaded.")
    return JSONResponse(content={"html_url": html_url})


def remove_illegal_chars(file_name: str) -> str:
    """Remove illegal characters from the filename.

    Args:
        file_name: The filename to remove illegal characters from.

    Returns:
        Returns a string with the filename without illegal characters.
    """
    filename: str = file_name.replace(" ", ".")
    illegal_characters: list[str] = [
        '"',
        ",",
        ";",
        ":",
        "?",
        "{",
        "}",
        "「",
        "」",
        "@",
        "*",
        "/",
        "&",
        "#",
        "%",
        "^",
        "+",
        "<",
        "=",
        ">",
        "|",
        "△",
        "$",
    ]
    for character in illegal_characters:
        filename: str = filename.replace(character, "")
        logger.info("Removed illegal character: %s from filename", character)

    return filename


index_html: str = """
<html lang="en">

<body>
    <h1>discord-nice-embed</h1>
    <a href="/docs">Swagger UI - API documentation</a>
    <br />
    <a href="/redoc">ReDoc - Alternative API documentation</a>
    <form action="/uploadfiles/" enctype="multipart/form-data" method="post">
        <input name="file" type="file" />
        <input type="submit" value="Upload file" />
    </form>
</body>

</html>
"""


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def main(request: Request) -> str:  # noqa: ARG001
    """Our index view.

    You can upload files here.

    Args:
        request: Our request.

    Returns:
        HTMLResponse: Our index.html page.
    """
    return index_html
