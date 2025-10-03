"""Shared data models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class PresenceRecord:
    """Represents a collected presence data point."""

    date: str
    presence: str

    @classmethod
    def from_datetime(cls, moment: datetime, presence: str) -> "PresenceRecord":
        return cls(date=moment.date().isoformat(), presence=presence)
