"""Logging setup module."""

import logging


def setup_logging(debug: bool) -> None:
    """Configure global logging format and level."""

    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
