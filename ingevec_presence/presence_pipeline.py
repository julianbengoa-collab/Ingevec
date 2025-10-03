"""Fetching and persistence pipeline for INGVEC presence data."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
import re
from typing import Iterable, List, Optional
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from .html_table_parser import ParsedTable, extract_tables
from .models import PresenceRecord
from .xlsx_writer import write_presence_workbook

PRESENCIA_URL = "https://www.bolsadesantiago.com/presencia_bursatil"
DATA_DIR = Path("data")
HISTORY_PATH = DATA_DIR / "presence_history.json"
EXCEL_PATH = DATA_DIR / "presencia_ingvec.xlsx"
TIMEZONE = ZoneInfo("America/Santiago")


def fetch_html(url: str = PRESENCIA_URL, timeout: int = 30) -> str:
    """Download the HTML page that contains the presence table."""

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/117.0 Safari/537.36"
        )
    }
    request = Request(url, headers=headers)
    with urlopen(request, timeout=timeout) as response:  # type: ignore[arg-type]
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def _resolve_presence_from_table(table: ParsedTable, ticker: str = "INGVEC") -> Optional[str]:
    ticker_row = table.find_row(ticker)
    if not ticker_row:
        return None

    presence_index = table.presence_column_index()
    if presence_index is not None and presence_index < len(ticker_row):
        value = ticker_row[presence_index].strip()
        if value:
            return value

    # Fallback: pick the cell immediately after the ticker, if present.
    try:
        ticker_index = next(
            idx for idx, cell in enumerate(ticker_row) if cell.upper() == ticker.upper()
        )
    except StopIteration:
        return None

    digit_pattern = re.compile(r"\d")

    for idx in range(ticker_index + 1, len(ticker_row)):
        candidate = ticker_row[idx].strip()
        if candidate and digit_pattern.search(candidate):
            return candidate

    for idx in range(ticker_index - 1, -1, -1):
        candidate = ticker_row[idx].strip()
        if candidate and digit_pattern.search(candidate):
            return candidate

    neighbour_indices = [ticker_index + 1, ticker_index - 1]
    for idx in neighbour_indices:
        if 0 <= idx < len(ticker_row):
            candidate = ticker_row[idx].strip()
            if candidate:
                return candidate
    return None


def extract_presence_value(html: str, ticker: str = "INGVEC") -> Optional[str]:
    """Parse the downloaded HTML and extract the presence value for the ticker."""

    for table in extract_tables(html):
        presence = _resolve_presence_from_table(table, ticker=ticker)
        if presence:
            return presence
    return None


def load_history(path: Path = HISTORY_PATH) -> List[PresenceRecord]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return [PresenceRecord(**item) for item in payload]


def save_history(records: Iterable[PresenceRecord], path: Path = HISTORY_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump([record.__dict__ for record in records], handle, ensure_ascii=False, indent=2)


def merge_record(records: List[PresenceRecord], new_record: PresenceRecord) -> List[PresenceRecord]:
    merged: List[PresenceRecord] = []
    found = False
    for record in records:
        if record.date == new_record.date:
            merged.append(new_record)
            found = True
        else:
            merged.append(record)
    if not found:
        merged.append(new_record)
    merged.sort(key=lambda item: item.date)
    return merged


def fetch_and_store_presence(now: Optional[datetime] = None) -> PresenceRecord:
    """Fetch the presence value and persist it to JSON and Excel outputs."""

    logger = logging.getLogger(__name__)
    moment = now or datetime.now(TIMEZONE)

    try:
        html = fetch_html()
    except (HTTPError, URLError, TimeoutError) as exc:  # pragma: no cover - network errors
        logger.error("Unable to retrieve presence information: %s", exc)
        raise

    presence_value = extract_presence_value(html)
    if not presence_value:
        logger.error("Presence value for INGVEC could not be found in the downloaded page.")
        raise ValueError("Could not locate presence value for INGVEC.")

    new_record = PresenceRecord.from_datetime(moment, presence_value)
    history = load_history()
    updated_history = merge_record(history, new_record)
    save_history(updated_history)

    write_presence_workbook(updated_history, EXCEL_PATH)
    logger.info("Stored presence value %s for %s", new_record.presence, new_record.date)
    return new_record


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(level=level, format="%(asctime)s [%(levelname)s] %(message)s")
