import os
import pathlib
import sys

from dotenv import load_dotenv


class Settings:
    description = (
        "Discord will only create embeds for videos and images if they are "
        "smaller than 8 mb. We can 'abuse' this by creating a .html that "
        "contains the 'twitter:player' HTML meta tag linking to the video."
    )
    # Load environment variables
    load_dotenv()

    # Check if user has added a domain to the environment.
    try:
        domain = os.environ["DOMAIN"]
    except KeyError:
        sys.exit("discord-embed: Environment variable 'DOMAIN' is missing!")

    # Remove trailing slash from domain
    if domain.endswith("/"):
        domain = domain[:-1]

    # Check if we have a folder for uploads.
    try:
        upload_folder = os.environ["UPLOAD_FOLDER"]
    except KeyError:
        sys.exit("Environment variable 'UPLOAD_FOLDER' is missing!")

    # Create upload_folder if it doesn't exist.
    pathlib.Path(upload_folder).mkdir(parents=True, exist_ok=True)

    # Remove trailing slash from upload_folder
    if upload_folder.endswith("/"):
        upload_folder = upload_folder[:-1]

    # Discord webhook URL
    try:
        webhook_url = os.environ["WEBHOOK_URL"]
    except KeyError:
        sys.exit("Environment variable 'WEBHOOK_URL' is missing!")
