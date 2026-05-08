from __future__ import annotations
from typing import Optional, Dict
from datetime import datetime
from dataclasses import dataclass, field
from models.task import Task
from models.temporal_task import TemporalTask

@dataclass
@Task.register
class Goal(TemporalTask):
    subgoals: Dict[str, Task] = field(default_factory=dict)
    completed_steps: int = 0
    
    def __str__(self):
        return self._build_tree_str(self)

    def _build_tree_str(self, node, prefix="", is_last=True) -> str:
        connector = "└── " if is_last else "├── "
        lines = [prefix + connector + str(node.get_title())]

        new_prefix = prefix + ("    " if is_last else "│   ")
        
        if (isinstance(node, Goal)):
            child_count = len(node.subgoals)

            for i, child in enumerate(node.subgoals.values()):
                is_last_child = (i == child_count - 1)
                lines.append(self._build_tree_str(child, new_prefix, is_last_child))

        return "\n".join(lines)

    def _check_index(self, index: int):
        if index is None or index < 0 or index >= len(self.subgoals):
            raise IndexError("Invalid subgoal index")
    
    def _check_time_period(self, goal: Task):
        if (
            (goal.get_deadline() and goal.get_deadline() > self.deadline) or
            (
                isinstance(goal, TemporalTask) and
                (
                    (goal.get_startline() and goal.get_startline() < self.startline) or
                    (goal.get_start_date() < self.start_date) or 
                    (goal.get_end_date() > self.end_date)
                )
            )
        ):
            raise ValueError(
                "Goal can not have a start_date, end_date, startline or deadline before or past this goal's start / end"
            )

    def to_dict(self):
        return {
            **super().to_dict(),
            "completed_steps": self.completed_steps,
            "subgoals": [subgoal.to_dict() for subgoal in self.subgoals.values()],
        }
        
    @classmethod
    def _from_dict(cls, data):
        if data is None:
            return None
        
        obj = super()._from_dict(data)

        obj.completed_steps = int(data["completed_steps"])
        obj.subgoals = {
            sub["title"]: Task.from_dict(sub)
            for sub in data["subgoals"]
        }

        return obj

    def get_completion_status(self):
        completed = self.completed
        for subgoal in self.subgoals.values():
            completed += subgoal.get_completion_status()
        return int(completed)

    def get_num_subgoals(self):
        count = len(self.subgoals)
        for subgoal in self.subgoals.values():
            if (isinstance(subgoal, Goal)):
                count += subgoal.get_num_subgoals()
        return count

    def get_subgoal_by_index(self, key: int):
        self._check_index(key)
        values = list(self.subgoals.values())
        self._check_index(key)
        return values[key]

    def get_subgoal_by_title(self, key: str):
        if key in self.subgoals:
            return self.subgoals[key]
        raise ValueError(f"Goal with title: {key} not found")

    def get_subgoals(self):
        return list(self.subgoals.values())

    def set_completed(self):
        for subgoal in self.subgoals.values():
            subgoal.set_completed()
        self.completed = True

    def add_subgoal(self, goal: Task):
        self._check_time_period(goal)
        self.subgoals[goal.title] = goal

    def remove_subgoal_by_index(self, key: int):
        self._check_index(key)
        del list(self.subgoals.values())[key]

    def remove_subgoal_by_title(self, key: str):
        if (key not in self.subgoals):
            raise ValueError(f"Goal with title: {key} not found")
        self.subgoals.pop(key)

    def complete_subgoal_by_index(self, key: int):
        self._check_index(key)
        list(self.subgoals.values())[int(key)].set_completed()

    def complete_subgoal_by_title(self, key: str):
        if (key in self.subgoals):
            self.subgoals[key].set_completed()
            return
        raise ValueError(f"Goal with title: ({key}) not found")

    def get_progress_fraction(self):
        return f"{self.get_completion_status()}/{self.get_num_subgoals()}"

    def get_progress_percent(self):
        if not self.subgoals:
            return 100.0
        return (self.get_completion_status() / self.get_num_subgoals()) * 100