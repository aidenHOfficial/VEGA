from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from datetime import datetime

class Task:
    _title: str
    _description: str
    _completed: bool = False
    _deadline: Optional[datetime] = None
    _registry = {}

    @classmethod
    def register(cls, subclass):
        cls._registry[subclass.__name__] = subclass
        return subclass

    def __init__(
            self, 
            title: str, 
            description: str, 
            deadline: Optional[datetime] = None):
        self._title = title
        self._description = description
        self._deadline = deadline

    def __eq__(self, other: Task):
        return self.to_dict() == other.to_dict()

    def __str__(self):
        return f"""Task(
                    \n\tTitle: {self._title}
                    \n\tDescription: {self._description}
                    \n\tDeadline: {self._deadline}
                    \n\tCompleted: {self._completed}
                \n)"""

    def __hash__(self):
        return hash(self.__str__())

    def to_dict(self):
        return {
            "_type": self.__class__.__name__,
            "_title": self._title,
            "_description": self._description,
            "_completed": self._completed,
            "_deadline": self._deadline.isoformat() if self._deadline is not None else None
        }
        
    @classmethod
    def from_dict(cls, data):
        task_type = data.get("_type", "Task")

        actual_cls = cls._registry.get(task_type)
        if actual_cls is None:
            raise ValueError(f"Unknown task type: {task_type}")

        return actual_cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data):
        if data is None:
            return None
        
        obj = cls.__new__(cls)
        
        obj._title = data["_title"]
        obj._description = data["_description"]
        obj._completed = bool(data["_completed"])
        obj._deadline = datetime.fromisoformat(data["_deadline"]) if data["_deadline"] else None
        
        return obj
        
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
        
Task._registry["Task"] = Task