from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv(verbose=True)

webhook_url: str = os.environ["WEBHOOK_URL"]
serve_domain: str = os.environ["SERVE_DOMAIN"].removesuffix("/")
upload_folder: str = os.environ["UPLOAD_FOLDER"].removesuffix("/")
Path(upload_folder).mkdir(parents=True, exist_ok=True)
