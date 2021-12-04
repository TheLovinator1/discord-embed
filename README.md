# discord-embed

Discord will only create embeds for videos and images if they are smaller than 8MB. We can "abuse" this by using the [twitter:image HTML meta tag](https://developer.twitter.com/en/docs/twitter-for-websites/cards/overview/markup).

This is useful when you send a video and want it to be playable in Discord.

## How it works

This program will create a .html that you will send instead of a .mp4 file. Discord will parse the HTML and create an embed for you. The embed will be the same as the one you would get if you send a .mp4 file.

## Installation

This implies that you have experience with Nginx. Don't be afraid to contact me if you need help.

* Install latest version of [git](https://git-scm.com/), [Python](https://www.python.org/), [Poetry](https://python-poetry.org/docs/#installation) and Nginx.
* Clone the repository or download the [source code](https://github.com/TheLovinator1/discord-nice-embed-maker-for-my-yoy/archive/refs/heads/master.zip) directly from GitHub.
* Install the dependencies using [Poetry](https://python-poetry.org/docs/#installation).
  * `poetry install`
* Rename .env.example to .env and fill in the required values.
* Copy discord-embed.service to /etc/systemd/system/discord-embed.service.
  * `sudo cp discord-embed.service /etc/systemd/system/discord-embed.service`
  * Change lovinator to your username.
  * Change DOMAIN to the domain where we will serve the files.
* There is a bundled nginx config file that can be used to serve the site.
  * `sudo cp nginx.conf /etc/nginx/`
* Start Nginx at boot.
  * `sudo systemctl enable --now nginx`
* Create directory for uploaded files.
  * `sudo mkdir /Uploads`
* Check what user is running Nginx, Arch is using http. Others could be www-data:
  * ps aux | grep nginx
* Change permissions of /Uploads directory. Change lovinator to your username and http to the user running Nginx.
  * `sudo chown -R lovinator:http /Uploads`
* Create log folder.
  * `sudo mkdir /var/log/discord-embed`
* Change permissions of /var/log/discord-embed directory. Change lovinator to your username.
  * `sudo chown -R lovinator:lovinator /var/log/discord-embed`
* Start the services.
  * `sudo systemctl enable --now  discord-embed.service`
  * `sudo systemctl enable --now discord-embed.socket`
* Check if the services are running.
  * `sudo systemctl status discord-embed.service`
  * `sudo systemctl status discord-embed.socket`
* Check logs for errors.
  * `cat /var/log/discord-embed/error.log` and `cat /var/log/discord-embed/access.log`

## Need help?

* Email: [tlovinator@gmail.com](mailto:tlovinator@gmail.com)
* Discord: TheLovinator#9276
* Steam: [TheLovinator](https://steamcommunity.com/id/TheLovinator/)
* Send an issue: [discord-embed/issues](https://github.com/TheLovinator1/discord-embed/issues)
