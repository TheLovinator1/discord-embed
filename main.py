import json
import os
import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from dhooks import Webhook
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse

hook = Webhook(os.environ["WEBHOOK"])

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

try:
    domain = os.environ["DOMAIN"]
except KeyError:
    sys.exit("Environment variable 'DOMAIN' is missing!")
if not domain.endswith("/"):
    domain += "/"


@app.post("/uploadfiles/")
async def upload_file(file: UploadFile = File(...)):
    content_type = file.content_type
    try:
        if content_type.startswith("video/"):
            output_folder = "Uploads/video"
            video_url = f"{domain}video/{file.filename}"
            Path(output_folder).mkdir(parents=True, exist_ok=True)

        elif content_type.startswith("image/"):
            output_folder = "Uploads/image"
            video_url = f"{domain}image/{file.filename}"
            Path(output_folder).mkdir(parents=True, exist_ok=True)

        elif content_type.startswith("text/"):
            output_folder = "Uploads/text"
            video_url = f"{domain}text/{file.filename}"
            Path(output_folder).mkdir(parents=True, exist_ok=True)

        else:
            output_folder = "Uploads/files"
            video_url = f"{domain}files/{file.filename}"
            Path(output_folder).mkdir(parents=True, exist_ok=True)

    except Exception as e:
        print(f"Failed to get content type/create folder: {e}")
        hook.send(f"Failed to get content type/create folder: {e}")

    print(file.filename)
    file_location = f"{output_folder}/{file.filename}"

    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    height, width = find_video_resolution(file_location)
    screenshot_url = get_first_frame(file_location, file.filename)

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


@app.get("/")
async def main():
    content = """
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
    return HTMLResponse(content=content)


def generate_html(url: str, width: int, height: int, screenshot: str, filename: str):
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

    filename += ".html"

    with open(f"Uploads/{filename}", "w", encoding="utf-8") as file:
        file.write(video_html)
    return f"{domain}{filename}"


def find_video_resolution(path_to_video):
    cmd = "ffprobe -v quiet -print_format json -show_streams "
    args = shlex.split(cmd)
    args.append(path_to_video)
    # run the ffprobe process, decode stdout into utf-8 & convert to JSON
    ffprobe_output = subprocess.check_output(args).decode("utf-8")
    ffprobe_output = json.loads(ffprobe_output)

    # find height and width
    height = ffprobe_output["streams"][0]["height"]
    width = ffprobe_output["streams"][0]["width"]

    return height, width


def get_first_frame(path_video, file_filename):
    cmd = f"ffmpeg -y -i {path_video} -vframes 1 Uploads/{file_filename}.jpg"
    args = shlex.split(cmd)

    subprocess.check_output(args).decode("utf-8")

    return f"{domain}{file_filename}.jpg"
