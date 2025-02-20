from __future__ import annotations

import logging

logger: logging.Logger = logging.getLogger("uvicorn.error")


def remove_illegal_chars(file_name: str) -> str:
    """Remove illegal characters from the filename.

    Args:
        file_name: The filename to remove illegal characters from.

    Returns:
        Returns a string with the filename without illegal characters.
    """
    filename: str = file_name.replace(" ", ".")
    illegal_characters: list[str] = [
        '"',
        ",",
        ";",
        ":",
        "?",
        "{",
        "}",
        "「",
        "」",
        "@",
        "*",
        "/",
        "&",
        "#",
        "%",
        "^",
        "+",
        "<",
        "=",
        ">",
        "|",
        "△",
        "$",
    ]
    for character in illegal_characters:
        filename: str = filename.replace(character, "")
        logger.info("Removed illegal character: %s from filename", character)

    return filename
