"""Website for uploading files, creating .HTMLs, and thumbnails.

This was created for Discord. You can use this to embed videos in Discord.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

import ffmpeg
from dhooks import Webhook
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import guess_lexer

from settings import Settings

hook = Webhook(Settings.webhook_url)
app = FastAPI(
    title="discord-nice-embed",
    description=Settings.description,
    version="0.0.1",
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


def normal_file_uploaded(file: UploadFile) -> Dict[str, str]:
    """Save file to disk and return URL.

    Args:
        file (UploadFile): Our file object.

    Returns:
        Dict[str, str]: Returns URL for file.
    """
    # Save file to disk.
    with open(f"{Settings.upload_folder}/{file.filename}", "wb+") as file_object:
        file_object.write(file.file.read())

    hook.send(f"{Settings.domain}/{file.filename} was uploaded.")
    return {"html_url": f"{Settings.domain}/{file.filename}"}


def video_file_uploaded(file: UploadFile) -> Dict[str, str]:
    """Save video to disk, generate HTML, thumbnail, and return the .HTML file instead of the file.

    Args:
        file (UploadFile): Our file object.

    Returns:
        Dict[str, str]: Returns URL for video.
    """
    # Make custom html for video files.

    # Create folder if it doesn't exist.
    Path(f"{Settings.upload_folder}/video").mkdir(parents=True, exist_ok=True)

    # Save file to disk.
    with open(f"{Settings.upload_folder}/video/{file.filename}", "wb+") as file_object:
        file_object.write(file.file.read())

    file_url = f"{Settings.domain}/video/{file.filename}"
    file_location = f"{Settings.upload_folder}/video/{file.filename}"
    height, width = find_video_resolution(file_location)
    screenshot_url = make_thumbnail_from_video(file_location, file.filename)
    html_url = generate_html_for_videos(
        filename=file.filename, url=file_url, width=width, height=height, screenshot=screenshot_url
    )
    hook.send(f"{Settings.domain}/{file.filename} was uploaded.")
    return {"html_url": f"{html_url}"}


def text_file_uploaded(file: UploadFile) -> Dict[str, str]:
    """Save file to disk and return URL.

    Args:
        file (UploadFile): Our file object.

    Returns:
        Dict[str, str]: Returns URL for file.
    """
    # Create folder if it doesn't exist.
    Path(f"{Settings.upload_folder}/text").mkdir(parents=True, exist_ok=True)

    save_location = f"{Settings.upload_folder}/text/{file.filename}"
    # Save file to disk.
    with open(save_location, "wb+") as file_object:
        file_object.write(file.file.read())

    with open(save_location, encoding="utf-8") as file_object:
        lines = file_object.read()
        colored_text = highlight(
            lines,
            guess_lexer(lines),  # Guess
            HtmlFormatter(
                style="fruity",  # Dark style
                linenos="table",  # Output line numbers as a table w/ two cells, one with line numbers, other with code
                full=True,  # Use inline styles instead of CSS classes.
                filename=f"{file.filename}",
            ),
        )

    with open(f"{Settings.upload_folder}/{file.filename}.html", "w", encoding="utf-8") as file_object:
        file_object.write(colored_text)

    html_url = f"{Settings.domain}/{file.filename}.html"

    hook.send(f"{html_url} was uploaded.")
    return {"html_url": f"{html_url}"}


@app.post("/uploadfiles/")
async def upload_file(file: UploadFile = File(...)) -> Dict[str, str]:
    """Page for uploading files.

    If it is a video, we need to make a HTML file, and a thumbnail otherwise we can just save
     the file and return the URL for it.
    If something goes wrong, we will send a message to Discord.

    Args:
        file (UploadFile): Our uploaded file.

    Returns:
        Dict[str, str]: Returns a dict with the filename or a link to the .html if it was a video.
    """
    try:
        if file.content_type.startswith("video/"):
            return video_file_uploaded(file)
        if (
            # TODO: This needs to be better and include more things.
            file.content_type.startswith("text/")
            or file.content_type.startswith("application/json")
            or file.content_type.startswith("application/x-sh")
            or file.content_type.startswith("application/xml")
        ):
            return text_file_uploaded(file)

        with open(f"{Settings.upload_folder}/{file.filename}", "wb+") as file_object:
            file_object.write(file.file.read())

        hook.send(f"{Settings.domain}/{file.filename} was uploaded.")
        return {"html_url": f"{Settings.domain}/{file.filename}"}
    except Exception as e:
        # TODO: Change response code to 400.
        hook.send(f"Something went wrong for {Settings.domain}/{file.filename}:\n{e}")
        return {"error": f"Something went wrong: {e}"}


@app.get("/", response_class=HTMLResponse)
async def main():
    """Our index view.

    You can upload files here.

    Returns:
        HTMLResponse: Returns HTML for site.
    """

    return """
<!DOCTYPE html>
<html>
<head>
<title>discord-nice-embed</title>
</head>
<body>
<a href="/docs">Swagger UI - API documentation</a>
<a href="/redoc">ReDoc - Alternative API documentation</a>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="file" type="file">
<input type="submit">
</form>
</body>
</html>
"""


def generate_html_for_videos(url: str, width: int, height: int, screenshot: str, filename: str) -> str:
    """Generate HTML for video files.

    This is what we will send to other people on Discord.
    You can remove the .html with your web server so the link will look normal.
    For example, with nginx, you can do this(note the $uri.html):
    location / {
            try_files $uri $uri/ $uri.html;
    }


    Args:
        url (str): URL for the video. This is accessible from the browser.
        width (int): This is the width of the video.
        height (int): This is the height of the video.
        screenshot (str): URL for screenshot. This is what you will see in Discord.
        filename (str): Original video filename. We will append .html to the filename.

    Returns:
        str: [description]
    """
    video_html = f"""
    <!DOCTYPE html>
    <html>
    <!-- Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -->
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
    html_url = f"{Settings.domain}/{filename}"

    # Take the filename and append .html to it.
    filename += ".html"

    with open(f"{Settings.upload_folder}/{filename}", "w", encoding="utf-8") as file:
        file.write(video_html)

    return html_url


def find_video_resolution(path_to_video: str) -> tuple[int, int]:
    """Find video resolution.

    Args:
        path_to_video (str): Path to video file.

    Returns:
        tuple[int, int]: Returns height and width.
    """
    probe = ffmpeg.probe(path_to_video)
    video_stream = next(
        (stream for stream in probe["streams"] if stream["codec_type"] == "video"),
        None,
    )
    if video_stream is None:
        print("No video stream found", file=sys.stderr)
        sys.exit(1)

    width = int(video_stream["width"])
    height = int(video_stream["height"])

    return height, width


def make_thumbnail_from_video(path_video: str, file_filename: str) -> str:
    """Make thumbnail for Discord. This is a screenshot of the video.

    Args:
        path_video (str): Path where video file is stored.
        file_filename (str): File name for URL.

    Returns:
        str: Returns thumbnail filename.
    """
    (
        ffmpeg.input(path_video, ss="1")  # Take a screenshot at 1 second.
        .output(f"{Settings.upload_folder}/{file_filename}.jpg", vframes=1)  # Output to file.
        .overwrite_output()  # Overwrite output.
        .run()  # Run.
    )
    # Return URL for thumbnail.
    return f"{Settings.domain}/{file_filename}.jpg"
