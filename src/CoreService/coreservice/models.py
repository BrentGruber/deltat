from enum import Enum
from pydantic import BaseModel
from datetime import datetime

class StatusEnum(str, Enum):
    active = "active"
    paused = "paused"
    complete = "complete"

class Task(BaseModel):
    id: str
    name: str = None
    start_time: datetime = datetime.utcnow()
    end_time: datetime = datetime.utcnow()
    status: StatusEnum = StatusEnum.active
    focus: int
    notes: str
    tags: list[str] = []