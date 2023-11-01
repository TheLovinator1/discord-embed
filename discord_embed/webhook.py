from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from discord_webhook import DiscordWebhook

from discord_embed import settings

if TYPE_CHECKING:
    from requests import Response

logger: logging.Logger = logging.getLogger(__name__)


def send_webhook(message: str) -> None:
    """Send a webhook to Discord.

    Args:
        message: The message to send.
    """
    webhook: DiscordWebhook = DiscordWebhook(
        url=settings.webhook_url,
        content=message or "discord-nice-embed: No message was provided.",
        rate_limit_retry=True,
    )
    response: Response = webhook.execute()
    if not response.ok:
        logger.critical("Webhook failed to send\n %s\n %s", response, message)
