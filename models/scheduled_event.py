from dataclasses import dataclass

from models.event import Event
from models.time_interval import TimeInterval

@dataclass(slots=True)
class ScheduledEvent:
    event: Event
    interval: TimeInterval