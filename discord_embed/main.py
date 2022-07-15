import datetime
import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin

import ffmpeg
import requests
from discord_webhook import DiscordWebhook
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from discord_embed import settings

DESCRIPTION = (
    "Discord will only create embeds for videos and images if they are"
    " smaller than 8 mb. We can 'abuse' this by creating a .html that"
    " contains the 'twitter:player' HTML meta tag linking to the video."
)
app = FastAPI(
    title="discord-nice-embed",
    description=DESCRIPTION,
    version="1.0.0",
    contact={
        "name": "Joakim Hellsén",
        "url": "https://github.com/TheLovinator1",
        "email": "tlovinator@gmail.com",
    },
    license_info={
        "name": "GPL-3.0",
        "url": "https://www.gnu.org/licenses/gpl-3.0.txt",
    },
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@dataclass
class FileModel:
    filename: str
    file_location: str


@dataclass
class Resolution:
    height: int
    width: int


def remove_illegal_characters(filename: str) -> str:
    filename = filename.replace(" ", ".")
    illegal_characters = [
        "*",
        '"',
        "<",
        ">",
        "△",
        "「",
        "」",
        "{",
        "}",
        "|",
        "^",
        ";",
        "/",
        "?",
        ":",
        "@",
        "&",
        "=",
        "+",
        "$",
        ",",
    ]
    for character in illegal_characters:
        filename = filename.replace(character, "")

    return filename


def generate_html_for_videos(url: str, width: int, height: int, screenshot: str, filename: str) -> str:
    video_html = f"""
    <!DOCTYPE html>
    <html>
    <!-- Generated at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -->
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

    file_path = os.path.join(settings.upload_folder, filename + ".html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(video_html)

    return urljoin(settings.serve_domain, filename)


def send_webhook(message: str) -> None:
    webhook = DiscordWebhook(
        url=settings.webhook_url,
        content=message,
        rate_limit_retry=True,
    )
    response: requests.Response = webhook.execute()
    if not response.ok:
        error_msg = f"Error: {response.text!r} ({response.status_code!r})\nMessage: {message!r}"
        print(error_msg)
        send_webhook(error_msg)


def video_resolution(path_to_video: str) -> Resolution | None:
    probe = ffmpeg.probe(path_to_video)
    video_stream = next((stream for stream in probe["streams"] if stream["codec_type"] == "video"), None)

    if video_stream is None:
        return None

    return Resolution(
        height=int(video_stream["height"]),
        width=int(video_stream["width"]),
    )


def make_thumbnail(path_video: str, file_filename: str) -> str | None:
    thumbnail = os.path.join(settings.upload_folder, file_filename + ".jpg")
    ffmpeg.input(path_video, ss="1").output(thumbnail, vframes=1).overwrite_output().run()

    if not os.path.isfile(thumbnail):
        return None

    return urljoin(settings.serve_domain, file_filename + ".jpg")


def save_to_disk(file: UploadFile) -> FileModel:
    folder_video = os.path.join(settings.upload_folder, "video")
    Path(folder_video).mkdir(parents=True, exist_ok=True)

    filename = remove_illegal_characters(file.filename)
    file_location = os.path.join(folder_video, filename)
    with open(file_location, "wb+") as f:
        f.write(file.file.read())

    return FileModel(filename, file_location)


async def if_video_file(file: UploadFile) -> HTMLResponse:
    video_file: FileModel = save_to_disk(file)

    resolution = video_resolution(video_file.file_location)
    if resolution is None:
        send_webhook(f"ERROR: Failed to find resolution for {video_file.file_location!r}")
        return HTMLResponse(status_code=400, content="Failed to find resolution")

    thumbnail_url = make_thumbnail(video_file.file_location, video_file.filename)
    if thumbnail_url is None:
        send_webhook(f"ERROR: Failed to make thumbnail for {video_file.file_location!r}")
        return HTMLResponse(status_code=400, content="Failed to make thumbnail")

    file_url = os.path.join(settings.serve_domain, "video", video_file.filename)
    html_url = generate_html_for_videos(
        url=file_url,
        width=resolution.width,
        height=resolution.height,
        screenshot=thumbnail_url,
        filename=video_file.filename,
    )

    send_webhook(f"{html_url!r} was uploaded.")

    return {"html_url": html_url}


@app.post("/uploadfiles/")
async def upload_file(file: UploadFile = File(...)) -> HTMLResponse:
    if file.content_type.startswith("video/"):
        return await if_video_file(file)

    filename = remove_illegal_characters(file.filename)
    file_location = os.path.join(settings.upload_folder, filename)
    with open(file_location, "wb+") as f:
        f.write(file.file.read())

    html_url = urljoin(settings.serve_domain, filename)
    send_webhook(f"{html_url!r} was uploaded.")

    return {"html_url": html_url}


@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
