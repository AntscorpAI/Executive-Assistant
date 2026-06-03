from pathlib import Path

import yaml

from app.core.config import settings


class AuditCatalog:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or settings.project_root / "config" / "audit_types.yaml"

    def load(self) -> dict:
        if not self.path.exists():
            return {}
        with self.path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        return data

    def get(self, audit_type: str) -> dict:
        return self.load().get(audit_type, {})


audit_catalog = AuditCatalog()
