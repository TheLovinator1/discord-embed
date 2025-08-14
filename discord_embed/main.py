from __future__ import annotations

import datetime
import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Annotated
from urllib.parse import urljoin

import av
import sentry_sdk
from discord_webhook import DiscordWebhook
from dotenv import load_dotenv
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse

if TYPE_CHECKING:
    from av.container import InputContainer
    from av.stream import Stream
    from requests import Response

# Load environment variables
load_dotenv(verbose=True)

webhook_url: str = os.environ["WEBHOOK_URL"]
serve_domain: str = os.environ["SERVE_DOMAIN"].removesuffix("/")
upload_folder: str = os.environ["UPLOAD_FOLDER"].removesuffix("/")
Path(upload_folder).mkdir(parents=True, exist_ok=True)


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
        if character in filename:
            logger.info("Removed illegal character: %s from filename", character)

    return filename


def video_resolution(path_to_video: str) -> tuple[int, int]:
    """Find video resolution.

    Args:
        path_to_video: Path to the video file.

    Raises:
        ValueError: If the video file cannot be opened.

    Returns:
        Returns video resolution as a tuple (width, height).
    """
    container: InputContainer = av.open(path_to_video)

    video_stream: Stream | None = next((s for s in container.streams if s.type == "video"), None)
    container.close()

    if video_stream is None:
        msg = "No video stream found"
        raise ValueError(msg)

    width = int(video_stream.codec_context.width)  # pyright: ignore[reportAttributeAccessIssue]
    height = int(video_stream.codec_context.height)  # pyright: ignore[reportAttributeAccessIssue]

    return width, height


def make_thumbnail(path_video: str, file_filename: str) -> str:
    """Make thumbnail for Discord using PyAV.

    Args:
        path_video: Path where video file is stored.
        file_filename: File name for URL.

    Returns:
        Thumbnail URL.
    """
    output_path: Path = Path(upload_folder) / f"{file_filename}.jpg"

    with av.open(file=path_video) as container:
        stream: av.VideoStream = container.streams.video[0]
        stream.codec_context.skip_frame = "NONKEY"
        frame: av.VideoFrame = next(container.decode(stream))

        frame.to_image().save(output_path)

    logger.info("Thumbnail created: %s", output_path)
    return f"{serve_domain}/{file_filename}.jpg"


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
    save_folder_video = Path(upload_folder, "video")
    Path(save_folder_video).mkdir(parents=True, exist_ok=True)

    # Replace spaces with dots and remove illegal characters
    filename: str = file.filename.replace(" ", ".")
    filename = remove_illegal_chars(filename)
    filename = filename.strip()

    # Save the uploaded file to disk.
    file_location = Path(save_folder_video, filename)
    with Path.open(file_location, "wb+") as f:
        f.write(file.file.read())

    file_url: str = f"{serve_domain}/video/{filename}"
    width, height = video_resolution(str(file_location))
    screenshot_url: str = make_thumbnail(str(file_location), filename)
    html_url: str = generate_html_for_videos(
        url=file_url,
        width=width,
        height=height,
        screenshot=screenshot_url,
        filename=filename,
    )
    logger.info("Generated HTML URL: %s", html_url)
    logger.debug("Video file location: %s", str(file_location))
    logger.debug("Video filename: %s", filename)

    return html_url


def send_webhook(message: str) -> None:
    """Send a webhook to Discord.

    Args:
        message: The message to send.
    """
    logger.info("Sending webhook with message: %s", message)
    webhook: DiscordWebhook = DiscordWebhook(
        url=webhook_url,
        content=message or "discord-nice-embed: No message was provided.",
        rate_limit_retry=True,
    )
    response: Response = webhook.execute()
    if not response.ok:
        logger.critical("Webhook failed to send\n %s\n %s", response, message)


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
    time_now: datetime.datetime = datetime.datetime.now(tz=datetime.timezone.utc)
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
    html_url: str = urljoin(serve_domain, filename)

    # Take the filename and append .html to it.
    filename += ".html"

    file_path = Path(upload_folder, filename)
    with Path.open(file_path, "w", encoding="utf-8") as f:
        f.write(video_html)

    logger.info("Generated HTML file: %s", html_url)
    logger.info("Saved HTML file to disk: %s", file_path)
    logger.info("Screenshot URL: %s", screenshot)
    logger.info("Video URL: %s", url)
    logger.info("Video resolution: %dx%d", width, height)
    logger.info("Filename: %s", filename)
    logger.info("Domain: %s", serve_domain)
    logger.info("HTML URL: %s", html_url)
    logger.info("Time now: %s", time_now_str)

    return html_url
