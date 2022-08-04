"""Our site has one POST endpoint for uploading videos and one GET
endpoint for getting the HTML. Images are served from a web server."""
from typing import Dict
from urllib.parse import urljoin

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from discord_embed import settings
from discord_embed.video_file_upload import do_things
from discord_embed.webhook import send_webhook

app = FastAPI(
    title="discord-nice-embed",
    description=settings.DESCRIPTION,
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

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.post("/uploadfiles/")
async def upload_file(file: UploadFile = File(...)) -> Dict[str, str]:
    """Page for uploading files.

    If it is a video, we need to make an HTML file, and a thumbnail
    otherwise we can just save the file and return the URL for it.
    If something goes wrong, we will send a message to Discord.

    Args:
        file: Our uploaded file.

    Returns:
        Returns a dict with the filename, or a link to the .html if it was a video.
    """
    domain_url = ""
    if file.content_type.startswith("video/"):
        return await do_things(file)

    filename = await remove_illegal_chars(file.filename)

    with open(f"{settings.upload_folder}/{filename}", "wb+") as f:
        f.write(file.file.read())

    domain_url = urljoin(settings.serve_domain, filename)
    send_webhook(f"{domain_url} was uploaded.")
    return {"html_url": domain_url}


async def remove_illegal_chars(filename: str) -> str:
    """Remove illegal characters from the filename.

    Space is replaced with a dot.
    "*, ", <, >, △, 「, 」, {, }, |, ^, ;, /, ?, :, @, &, =, +, $, ,," are removed.


    Args:
        filename: The filename to remove illegal characters from.

    Returns:
        Returns a string with the filename without illegal characters.
    """

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


@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    """Our index view.

    You can upload files here.

    Returns:
        HTMLResponse: Returns HTML for site.
    """

    return templates.TemplateResponse("index.html", {"request": request})
