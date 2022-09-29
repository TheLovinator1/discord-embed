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

## Need help?

- Email: [tlovinator@gmail.com](mailto:tlovinator@gmail.com)
- Discord: TheLovinator#9276
- Send an issue: [discord-embed/issues](https://github.com/TheLovinator1/discord-embed/issues)
