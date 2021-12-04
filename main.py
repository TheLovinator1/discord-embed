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

# Remove trailing slash from domain.
if domain.endswith("/"):
    domain = domain[:-1]

# Check if we have a folder for uploads.
try:
    upload_folder = os.environ["UPLOAD_FOLDER"]
except KeyError:
    sys.exit("discord-embed: Environment variable 'UPLOAD_FOLDER' is missing!")

# Remove trailing slash from path.
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
    if file.content_type.startswith("video/"):
        file_type = "video"

    elif file.content_type.startswith("image/"):
        file_type = "image"

    elif file.content_type.startswith("text/"):
        file_type = "text"

    else:
        file_type = "files"

    output_folder = f"{upload_folder}/{file_type}"

    # Create folder if it doesn't exist.
    Path(output_folder).mkdir(parents=True, exist_ok=True)

    file_url = f"{domain}/{file_type}/{file.filename}"
    file_location = f"{output_folder}/{file.filename}"

    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    # Get file size.
    file_size = os.stat(file_location).st_size

    height, width = find_video_resolution(file_location)

    # Only create thumbnail if file is a video.
    if file_type == "video":
        screenshot_url = make_thumbnail_from_video(file_location, file.filename)
    if file_type == "image" and file_size < 8000000:
        print(f"File is smaller than 8mb: {file_size}")
        screenshot_url = make_thumbnail_from_image(file_location, file.filename)

    html_url = generate_html(file_url, width, height, screenshot_url, file.filename)
    json_output = {
        "html_url": f"{html_url}",
        "video_url": f"{file_url}",
        "width": f"{width}",
        "height": f"{height}",
        "filename": f"{file.filename}",
        "content_type": f"{file.content_type}",
        "file_type": f"{file_type}",
        "current_time": f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    }

    # Only add screenshot_url if it exists.
    if screenshot_url:
        json_output.update({"screenshot_url": f"{screenshot_url}"})

    return json_output


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
    html_url = f"{domain}/{filename}"
    filename += ".html"

    with open(f"{upload_folder}/{filename}", "w", encoding="utf-8") as file:
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
    ffmpeg.input(path_video, ss="1").output(f"{upload_folder}/{file_filename}.jpg", vframes=1).run()

    return f"{domain}/{file_filename}.jpg"


def make_thumbnail_from_image(path_image: str, file_filename: str) -> str:
    """Make thumbnail for Discord. This is for images.
    This will change the image to 440 pixels wide and keep the aspect ratio.

    Args:
        path_image (str): Path where image is stored.
        file_filename (str): File name for URL.

    Returns:
        str: Returns thumbnail filename.
    """
    ffmpeg.input(path_image).output(f"{upload_folder}/{file_filename}", vf="scale=440:-1").run()

    return f"{domain}/{file_filename}"
