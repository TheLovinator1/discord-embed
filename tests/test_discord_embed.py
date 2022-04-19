from discord_embed import __version__, settings


def test_version():
    """Test that version is correct."""
    assert __version__ == "0.1.0"


def test_domain_ends_with_slash():
    """Test that domain ends with slash."""
    assert not settings.domain.endswith("/")
