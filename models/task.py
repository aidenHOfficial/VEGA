from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from uuid import UUID, uuid4

@dataclass(eq=True)
class Task:
    title: str
    description: str
    completed: bool = False
    deadline: Optional[datetime] = None
    registry = {}

    @classmethod
    def register(cls, subclass):
        cls.registry[subclass.__name__] = subclass
        return subclass

    def __hash__(self):
        return hash((self.title, self.description, self.completed, self.deadline))
    
    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "deadline": self.deadline.isoformat() if self.deadline is not None else None
        }
        
    @classmethod
    def from_dict(cls, data):
        task_type = data.get("type", "Task")

        actual_cls = cls.registry.get(task_type)
        if actual_cls is None:
            raise ValueError(f"Unknown task type: {task_type}")

        return actual_cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data):
        if data is None:
            return None
        
        obj = cls.__new__(cls)
        
        obj.title = data["title"]
        obj.description = data["description"]
        obj.completed = bool(data["completed"])
        obj.deadline = datetime.fromisoformat(data["deadline"]) if data["deadline"] else None
        
        return obj
        
    def get_completion_status(self):
        return self.completed

    def get_title(self):
        return self.title

    def get_description(self):
        return self.description

    def get_deadline(self):
        return self.deadline

    def set_completed(self):
        self.completed = True
        
Task.registry["Task"] = Task