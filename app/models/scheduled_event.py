from dataclasses import dataclass

from app.models.event import Event
from app.models.time_interval import TimeInterval

@dataclass(slots=True)
class ScheduledEvent:
    event: Event
    interval: TimeInterval