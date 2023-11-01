# discord-embed

Discord will only create embeds for videos and images if they are smaller than 8MB. We can "abuse" this by using
the [twitter:image HTML meta tag](https://developer.twitter.com/en/docs/twitter-for-websites/cards/overview/markup).

This is useful when you send a video and want it to be playable in Discord.

## How it works

This program will create a .html that you will send instead of a .mp4 file. Discord will parse the HTML and create an
embed for you. The embed will be the same as the one you would get if you send a .mp4 file.

## Environment variables

| Variable      | Description                                                      |
|---------------|------------------------------------------------------------------|
| SERVE_DOMAIN  | Domain where we server files from, not where we upload files to. |
| UPLOAD_FOLDER | Path to the directory where we store files.                      |
| WEBHOOK_URL   | Discord Webhook URL                                              |

## How to use

This project is meant to be used with Docker. You can find a docker-compose.yml file in this repository.

We have to do some URL rewriting to make this work. You can find examples for Nginx and Caddy below.

## Nginx

You have two example files here: [embed.subdomain.conf](embed.subdomain.conf) and [i.subdomain.conf](i.subdomain.conf)

* embed.subdomain.conf
  * This is the file you will use for the subdomain where you will upload files to.
* i.subdomain.conf:
  * This is the file you will use for the subdomain where you will serve files from.

## Caddy

```yaml
# SERVE_DOMAIN = i.example.com
# UPLOAD_FOLDER = /var/www/embed
embed.example.com {
  reverse_proxy * http://discord-embed:5000 # The Docker container where discord-embed runs
}

i.example.com {
  root * /var/www/embed
  try_files {uri} {uri}/ {uri}.html
  file_server
}
```

## ShareX

There is a [ShareX.sxcu](ShareX.sxcu) file in this repository. You can import it into ShareX and use it to upload files
to your server. You will have to change the RequestURL to your own domain. (The domain where discord-embed runs).

It will return a JSON object with the URL to the file. This is the URL you will send in Discord.

```JSON
{
  "Version": "14.1.1",
  "Name": "Discord Embed",
  "DestinationType": "FileUploader",
  "RequestMethod": "POST",
  "RequestURL": "https://embed.example.com/uploadfiles/",
  "Body": "MultipartFormData",
  "FileFormName": "file",
  "URL": "{json:html_url}"
}
```
