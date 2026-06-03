from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass
class MeetingCommandResult:
    transcript: str
    intent: str
    action_items: list[str]
    opened_document: str | None = None
    section_ref: str | None = None
    audit_type: str | None = None


class MeetingAssistant:
    def parse_command(self, transcript: str) -> MeetingCommandResult:
        lower = transcript.lower()
        action_items: list[str] = []
        opened_document: str | None = None
        section_ref: str | None = None
        intent = "general"
        audit_type: str | None = None

        section_match = re.search(r"section\s+([0-9]+(?:\.[0-9]+)*)", lower)
        if section_match:
            section_ref = section_match.group(1)

        for code in ["9001", "14001", "27001", "45001", "42001", "20000"]:
            if code in lower:
                audit_type = f"iso_{code}"
                break

        if "open" in lower and "checklist" in lower:
            opened_document = "Requested checklist"
            intent = "open_checklist"
            action_items.append("Retrieve checklist and share context")
        if "show" in lower and "schedule" in lower:
            action_items.append("Review audit schedule")
            intent = "show_schedule"
        if "next week" in lower and intent == "show_schedule":
            action_items.append("Filter audits for next week")
        if "follow up" in lower:
            action_items.append("Create follow-up task")
            if intent == "general":
                intent = "task_followup"
        if section_ref:
            action_items.append(f"Retrieve section {section_ref} from requested document")
            if intent == "general":
                intent = "show_section"

        return MeetingCommandResult(
            transcript=transcript,
            intent=intent,
            action_items=action_items,
            opened_document=opened_document,
            section_ref=section_ref,
            audit_type=audit_type,
        )


meeting_assistant = MeetingAssistant()
