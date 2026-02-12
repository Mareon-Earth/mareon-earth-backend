from __future__ import annotations

from enum import Enum

class DrydockProjectStatus(str, Enum):
    PLANNING = "planning"
    TENDER = "tender"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
