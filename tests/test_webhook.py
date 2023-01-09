from discord_embed.webhook import send_webhook


def test_send_webhook():
    """Test send_webhook() works."""
    send_webhook("Running Pytest")
