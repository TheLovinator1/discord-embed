from __future__ import annotations

import nox

nox.options.default_venv_backend = "uv"


@nox.session(python=["3.9", "3.10", "3.11", "3.12", "3.13"])
def tests(session: nox.Session) -> None:
    """Run the test suite."""
    # pip install .
    session.install(".")
    session.install("pytest", "pytest-httpx")
    session.run("pytest")
