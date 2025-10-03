"""Command line entry point to fetch INGVEC presence and export to Excel."""

from __future__ import annotations

import argparse
import logging
from datetime import datetime

from ..presence_pipeline import configure_logging, fetch_and_store_presence


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--at",
        type=str,
        default=None,
        help=(
            "Optional ISO timestamp (America/Santiago) to record the measurement. "
            "Defaults to the current time."
        ),
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        help="Logging level (DEBUG, INFO, WARNING, ERROR).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    configure_logging(getattr(logging, args.log_level.upper(), logging.INFO))

    moment = None
    if args.at:
        moment = datetime.fromisoformat(args.at)

    record = fetch_and_store_presence(now=moment)
    logging.getLogger(__name__).info(
        "Presence for %s captured: %s", record.date, record.presence
    )


if __name__ == "__main__":
    main()
