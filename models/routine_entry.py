from __future__ import annotations
from datetime import timedelta
from dataclasses import dataclass
from models.task import Task
from models.temporal_task import TemporalTask

@dataclass
class RoutineEntry:
    task: TemporalTask
    duration: timedelta

    def __hash__(self):
        return hash((
            self.task,
            self.duration
        ))

    def to_dict(self):
        return {
            "task": self.task.to_dict(),
            "duration": self.duration.total_seconds()
        }
        
    @classmethod
    def from_dict(cls, data):
        if data is None:
            return None
        
        obj = cls.__new__(cls)
        
        obj.task = Task.from_dict(data["task"])
        obj.duration = timedelta(seconds=data["duration"])
        
        return obj