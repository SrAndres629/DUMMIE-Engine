from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field


MISSION_STATUSES = {"created", "running", "paused", "blocked", "completed", "failed"}
_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


@dataclass
class MissionRuntimeContract:
    mission_id: str
    phase_id: str
    status: str = "created"
    resume_token: str = ""
    recovery_packet_ref: str = ""
    next_action_ref: str = ""
    private_reasoning_refs: list[str] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        _validate_safe_id("mission_id", self.mission_id)
        _validate_safe_id("phase_id", self.phase_id)
        if self.status not in MISSION_STATUSES:
            raise ValueError(f"Unsupported mission runtime status: {self.status}")
        if not self.resume_token:
            self.resume_token = deterministic_resume_token(self.mission_id, self.phase_id, self.status)
        self.private_reasoning_refs = []

    def to_dict(self) -> dict[str, str]:
        payload = asdict(self)
        payload.pop("private_reasoning_refs", None)
        return payload

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=True, sort_keys=True)


def deterministic_resume_token(mission_id: str, phase_id: str, status: str = "created") -> str:
    payload = f"{mission_id}:{phase_id}:{status}".encode("utf-8")
    return "resume-" + hashlib.sha256(payload).hexdigest()[:24]


def _validate_safe_id(field_name: str, value: str) -> None:
    if not value or ".." in value or "/" in value or "\\" in value:
        raise ValueError(f"{field_name} rejected: path traversal is not allowed")
    if not _SAFE_ID.match(value):
        raise ValueError(f"{field_name} rejected: only letters, numbers, hyphen, and underscore are allowed")
