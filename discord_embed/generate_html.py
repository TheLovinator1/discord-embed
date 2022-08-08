"""Generate the HTML that makes this program useful.

This is what we will send to other people on Discord.
You can remove the .html with your web server, so the link will look normal.
For example, with nginx, you can do this(note the $uri.html):
location / {
        try_files $uri $uri/ $uri.html;
}
"""
import os
from datetime import datetime
from urllib.parse import urljoin

from discord_embed import settings


def generate_html_for_videos(url: str, width: int, height: int, screenshot: str, filename: str) -> str:
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
    domain = settings.serve_domain
    html_url: str = urljoin(domain, filename)

    # Take the filename and append .html to it.
    filename += ".html"

    file_path = os.path.join(settings.upload_folder, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(video_html)

    return html_url
