"""Website for uploading files and creating .HTMLs and thumbnails so we can embed files in Discord.
"""
import os
import sys
from datetime import datetime
from pathlib import Path

import ffmpeg
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse

load_dotenv()

app = FastAPI(
    title="discord-nice-embed",
    description="""
Discord will only create embeds for videos and images if they are smaller than
 8mb. We can "abuse" this by using the "twitter:image" HTML meta tag.
""",
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

# Check if user has added a domain to the environment.
try:
    domain = os.environ["DOMAIN"]
except KeyError:
    sys.exit("discord-embed: Environment variable 'DOMAIN' is missing!")

# Append / to domain if it's missing.
if not domain.endswith("/"):
    domain += "/"

# Check if we have a folder for uploads.
try:
    upload_folder = os.environ["UPLOAD_FOLDER"]
except KeyError:
    sys.exit("discord-embed: Environment variable 'UPLOAD_FOLDER' is missing!")

# Remove trailing slash from path
if upload_folder.endswith("/"):
    upload_folder = upload_folder[:-1]


@app.post("/uploadfiles/")
async def upload_file(file: UploadFile = File(...)):
    """Page for uploading files.

    Args:
        file (UploadFile): Our uploaded file. Defaults to File(...).

    Returns:
        HTMLResponse: Returns HTML for site.
    """
    content_type = file.content_type
    try:
        if content_type.startswith("video/"):
            output_folder = f"{upload_folder}/video"
            video_url = f"{domain}video/{file.filename}"
            Path(output_folder).mkdir(parents=True, exist_ok=True)

        elif content_type.startswith("image/"):
            output_folder = f"{upload_folder}/image"
            video_url = f"{domain}image/{file.filename}"
            Path(output_folder).mkdir(parents=True, exist_ok=True)

        elif content_type.startswith("text/"):
            output_folder = f"{upload_folder}/text"
            video_url = f"{domain}text/{file.filename}"
            Path(output_folder).mkdir(parents=True, exist_ok=True)

        else:
            output_folder = f"{upload_folder}/files"
            video_url = f"{domain}files/{file.filename}"
            Path(output_folder).mkdir(parents=True, exist_ok=True)

    except Exception as exception:  # pylint: disable=broad-except
        print(f"Failed to get content type/create folder: {exception}")

    file_location = f"{output_folder}/{file.filename}"

    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    height, width = find_video_resolution(file_location)
    screenshot_url = make_thumbnail(file_location, file.filename)

    html_url = generate_html(
        video_url,
        width,
        height,
        screenshot_url,
        file.filename,
    )

    return {
        "html_url": f"{html_url}",
        "video_url": f"{video_url}",
        "width": f"{width}",
        "height": f"{height}",
        "screenshot_url": f"{screenshot_url}",
        "filename": f"{file.filename}",
        "content_type": f"{content_type}",
    }


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
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="file" type="file">
<input type="submit">
</form>
</body>
</html>
"""


def generate_html(
    url: str,
    width: int,
    height: int,
    screenshot: str,
    filename: str,
) -> str:
    """Generate HTML for media files.

    This is what we will send to other people on Discord.
    You can remove the .html with your web server so the link will look normal.

    Args:
        url (str): URL for video.
        width (int): Video width.
        height (int): Video height.
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
    html_url = f"{domain}{filename}"
    filename += ".html"

    with open(f"Uploads/{filename}", "w", encoding="utf-8") as file:
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


def make_thumbnail(path_video: str, file_filename: str) -> str:
    """Make thumbnail for Discord.

    Args:
        path_video (str): Path where media file is stored.
        file_filename (str): File name for URL.

    Returns:
        str: Returns thumbnail filename.
    """
    out_filename = f"{domain}{file_filename}.jpg"
    ffmpeg.input(path_video, ss="1").output(f"Uploads/{file_filename}.jpg", vframes=1).run()

    return out_filename
