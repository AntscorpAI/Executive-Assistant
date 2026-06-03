from __future__ import annotations

from app.models.entities import Audit
from app.services.catalog import audit_catalog


class ReminderService:
    def build_auditor_digest(self, audits: list[Audit], heading: str) -> str:
        lines = [f"{heading}:"]
        for audit in audits:
            catalog_entry = audit_catalog.get(audit.audit_type.value)
            expectation = audit.expectations or catalog_entry.get("client_message", "Review the audit plan and required documentation.")
            lines.append(f"- {audit.start_at:%Y-%m-%d %H:%M} {audit.title} for {audit.client_name}")
            lines.append(f"  Expectation: {expectation}")
        return "\n".join(lines)

    def build_client_checklist(self, audit: Audit) -> str:
        catalog_entry = audit_catalog.get(audit.audit_type.value)
        required_documents = catalog_entry.get("required_documents", [])
        lines = [
            f"Client reminder for {audit.client_name}",
            f"Audit: {audit.title}",
            "Required documents:",
        ]
        lines.extend(f"- {item}" for item in required_documents)
        return "\n".join(lines)


reminder_service = ReminderService()
