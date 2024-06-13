from __future__ import annotations

import re

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar


class FilenameValidationError(Exception):
    pass


def validate_filename(file_path: Path, message_ref_id: str, timestamp: str) -> None:
    filename_vars = FilenameVars.from_filename(file_path.name)
    messagespec_vars = MessageSpecVars.from_messagespec(
        message_ref_id=message_ref_id,
        timestamp=timestamp,
    )

    if filename_vars.declaration_year != messagespec_vars.declaration_year:
        raise FilenameValidationError("Year inconsistent with content of file")

    if filename_vars.platform_id != messagespec_vars.platform_id:
        raise FilenameValidationError("Platform id inconsistent with content of file")

    if filename_vars.timestamp != messagespec_vars.timestamp:
        raise FilenameValidationError("Timestamp inconsistent with content of file")


def build_filename(message_ref_id: str, timestamp: str) -> str:
    ms_vars = MessageSpecVars.from_messagespec(
        message_ref_id=message_ref_id,
        timestamp=timestamp,
    )
    return f"DPIDAC7_{ms_vars.declaration_year}_{ms_vars.platform_id}_{ms_vars.declaration_id}_{ms_vars.timestamp}"


@dataclass
class ExpectedVars:
    declaration_year: str
    platform_id: str
    declaration_id: str
    timestamp: str


class FilenameVars(ExpectedVars):
    REGEX: ClassVar[str] = (
        r"^DPIDAC7_(?P<declaration_year>[0-9]{4})_(?P<platform_id>[0-9]{9})_"
        r"(?P<declaration_id>[0-9]{3})_(?P<timestamp>[0-9]{14}).xml$"
    )

    @classmethod
    def from_filename(cls, filename: str) -> FilenameVars:
        match = re.match(cls.REGEX, filename)
        if not match:
            raise FilenameValidationError("File does not match expected pattern")

        return cls(
            declaration_year=match.group("declaration_year"),
            platform_id=match.group("platform_id"),
            declaration_id=match.group("declaration_id"),
            timestamp=match.group("timestamp"),
        )


class MessageSpecVars(ExpectedVars):
    REGEX: ClassVar[str] = r"^OP_(?P<declaration_year>[0-9]{4})_(?P<platform_id>[0-9]{9})_"

    @classmethod
    def from_messagespec(cls, message_ref_id: str, timestamp: str) -> MessageSpecVars:
        match = re.match(cls.REGEX, message_ref_id)
        if not match:
            raise Exception

        return cls(
            declaration_year=match.group("declaration_year"),
            platform_id=match.group("platform_id"),
            declaration_id="001",
            timestamp=re.sub("[^0-9]", "", timestamp)[:14],
        )
