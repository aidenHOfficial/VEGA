from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from dataclasses import dataclass

@dataclass
class Task:
    _title: str
    _description: str
    _completed: bool = False
    _deadline: Optional[datetime] = None

    def __init__(self, title: str, description: str, deadline: Optional[datetime] = None):
        self._title = title
        self._description = description
        self._deadline = deadline

    def __eq__(self, other):
        if TYPE_CHECKING:
            from models.temporal_task import TemporalTask
            if not isinstance(other, TemporalTask):
                return NotImplemented
        return (
            self._title == other._title and 
            self._description == other._description and
            self._deadline == other._deadline and
            self._completed == other._completed
        )
    
    def __str__(self):
        return f"Task(\n\tTitle: {self._title}\n\tDescription: {self._description}\n\tDeadline: {self._deadline}\n\tCompleted: {self._completed}\n)"
    
    def __hash__(self):
        return hash(self.__str__())

    def get_completion_status(self):
        return self._completed
    
    def get_title(self):
        return self._title
    
    def get_description(self):
        return self._description

    def get_deadline(self):
        return self._deadline
    
    def set_completed(self):
        self._completed = True