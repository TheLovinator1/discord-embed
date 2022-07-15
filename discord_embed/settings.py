"""Read settings from environment variables."""
import os
import pathlib
import sys

from dotenv import load_dotenv

load_dotenv()

try:
    serve_domain = os.environ["SERVE_DOMAIN"]
except KeyError:
    sys.exit("discord-embed: Environment variable 'SERVE_DOMAIN' is missing!")
if serve_domain.endswith("/"):
    serve_domain = serve_domain[:-1]

try:
    upload_folder = os.environ["UPLOAD_FOLDER"]
except KeyError:
    sys.exit("Environment variable 'UPLOAD_FOLDER' is missing!")
pathlib.Path(upload_folder).mkdir(parents=True, exist_ok=True)
if upload_folder.endswith("/"):
    upload_folder = upload_folder[:-1]

try:
    webhook_url = os.environ["WEBHOOK_URL"]
except KeyError:
    sys.exit("Environment variable 'WEBHOOK_URL' is missing!")
