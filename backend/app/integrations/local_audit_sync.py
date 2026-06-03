from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import csv
import json


@dataclass
class LocalAuditRecord:
    client_name: str
    audit_type: str
    title: str
    start_at: str
    end_at: str
    auditor_email: str | None = None


class LocalAuditSync:
    def import_csv(self, path: Path) -> list[LocalAuditRecord]:
        records: list[LocalAuditRecord] = []
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                records.append(LocalAuditRecord(**row))
        return records

    def import_json(self, path: Path) -> list[LocalAuditRecord]:
        with path.open(encoding="utf-8") as handle:
            rows = json.load(handle)
        return [LocalAuditRecord(**row) for row in rows]


local_audit_sync = LocalAuditSync()
