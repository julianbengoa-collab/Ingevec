"""HTML table parsing helpers without external dependencies."""

from __future__ import annotations

from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import List, Optional


@dataclass
class ParsedTable:
    """Represents a parsed HTML table."""

    rows: List[List[str]] = field(default_factory=list)

    def presence_column_index(self) -> Optional[int]:
        """Return the index of the column that contains the word 'presencia'."""

        for row in self.rows[:5]:  # inspect only the first few rows
            for idx, cell in enumerate(row):
                if "presencia" in cell.lower():
                    return idx
        return None

    def find_row(self, ticker: str) -> Optional[List[str]]:
        """Find the first row that contains the provided ticker symbol."""

        ticker_upper = ticker.upper()
        for row in self.rows:
            for cell in row:
                if cell.upper() == ticker_upper:
                    return row
        return None


class TableHTMLParser(HTMLParser):
    """Extracts tables from an HTML document."""

    def __init__(self) -> None:
        super().__init__()
        self.tables: List[ParsedTable] = []
        self._table_stack: List[ParsedTable] = []
        self._current_row: Optional[List[str]] = None
        self._current_cell: Optional[str] = None

    # HTMLParser overrides -------------------------------------------------
    def handle_starttag(self, tag: str, attrs):  # type: ignore[override]
        if tag == "table":
            table = ParsedTable()
            self._table_stack.append(table)
        elif tag == "tr" and self._table_stack:
            self._current_row = []
        elif tag in {"td", "th"} and self._current_row is not None:
            self._current_cell = ""

    def handle_data(self, data: str) -> None:  # type: ignore[override]
        if self._current_cell is not None:
            self._current_cell += data

    def handle_endtag(self, tag: str) -> None:  # type: ignore[override]
        if tag in {"td", "th"} and self._current_cell is not None and self._current_row is not None:
            text = " ".join(self._current_cell.split())
            self._current_row.append(text)
            self._current_cell = None
        elif tag == "tr" and self._current_row is not None and self._table_stack:
            if any(cell for cell in self._current_row):
                self._table_stack[-1].rows.append(self._current_row)
            self._current_row = None
        elif tag == "table" and self._table_stack:
            table = self._table_stack.pop()
            if table.rows:
                self.tables.append(table)


def extract_tables(html: str) -> List[ParsedTable]:
    """Parse an HTML string and return the extracted tables."""

    parser = TableHTMLParser()
    parser.feed(html)
    return parser.tables
