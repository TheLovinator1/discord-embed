"""Send webhook to Discord."""
from discord_webhook import DiscordWebhook

from discord_embed import settings


def send_webhook(message: str) -> None:
    """Send webhook to Discord.

    Args:
        message: The message to send.
    """
    webhook = DiscordWebhook(
        url=settings.webhook_url,
        content=message,
        rate_limit_retry=True,
    )
    webhook.execute()
