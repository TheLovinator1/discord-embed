from discord_embed import __version__
from discord_embed.settings import Settings


def test_version():
    assert __version__ == "0.1.0"


def test_domain_ends_with_slash():
    assert not Settings.domain.endswith("/")
