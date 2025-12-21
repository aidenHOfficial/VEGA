from __future__ import annotations
from typing import Optional, Dict
from datetime import datetime
from dataclasses import dataclass, field
from models.task import Task
from models.temporal_task import TemporalTask

@dataclass
class Goal(TemporalTask):
    _subgoals: Dict[str, Task] = field(default_factory=dict)
    _completed_steps: int = 0
    
    def __init__(self, title: str, description: str, start_date: datetime, end_date: datetime, startline: Optional[datetime] = None, deadline: Optional[datetime] = None):
        super().__init__(title, description, start_date, end_date, start_date, end_date)

        self._subgoals = {}
        self._completed_steps = 0

    def __str__(self):
        return self._build_tree_str(self)

    def _build_tree_str(self, node, prefix="", is_last=True) -> str:
        connector = "└── " if is_last else "├── "
        lines = [prefix + connector + str(node.get_title())]

        new_prefix = prefix + ("    " if is_last else "│   ")
        
        if (isinstance(node, Goal)):
            child_count = len(node._subgoals)

            for i, child in enumerate(node._subgoals.values()):
                is_last_child = (i == child_count - 1)
                lines.append(self._build_tree_str(child, new_prefix, is_last_child))

        return "\n".join(lines)

    def _check_index(self, index):
        if index is None or index < 0 or index >= len(self._subgoals):
            raise IndexError("Invalid subgoal index")
    
    def _check_time_period(self, goal: Task):
        if (
            (goal.get_deadline() and goal.get_deadline() > self._deadline) or
            (
                isinstance(goal, TemporalTask) and
                (
                    (goal.get_startline() and goal.get_startline() < self._startline) or
                    (goal.get_start_date() < self._start_date) or 
                    (goal.get_end_date() > self._end_date)
                )
            )
        ):
            raise ValueError(
                "Goal can not have a start_date, end_date, startline or deadline before or past this goal's start / end"
            )
    
    def get_completion_status(self):
        completed = self._completed
        for subgoal in self._subgoals.values():
            completed += subgoal.get_completion_status()
        return int(completed)

    def get_num_subgoals(self):
        count = len(self._subgoals)
        for subgoal in self._subgoals.values():
            if (isinstance(subgoal, Goal)):
                count += subgoal.get_num_subgoals()
        return count

    def get_subgoal(self, key):
        if isinstance(key, int):
            self._check_index(key)
            values = list(self._subgoals.values())
            self._check_index(key)
            return values[key]
        elif isinstance(key, str):
            if key in self._subgoals:
                return self._subgoals[key]
            raise ValueError(f"Goal with title: {key} not found")
        raise TypeError("Key must be an int or str")
    
    def get_subgoals(self):
        return list(self._subgoals.values())

    def set_completed(self):
        for subgoal in self._subgoals.values():
            subgoal.set_completed()
        self._completed = True
    
    def add_subgoal(self, goal: Task):
        self._check_time_period(goal)

        self._subgoals[goal._title] = goal
        
        # self._check_completion()

    def remove_subgoal(self, key):
        if isinstance(key, int):
            self._check_index(key)
            del list(self._subgoals.values())[key]
        elif isinstance(key, str):
            if (key in self._subgoals):
                self._subgoals.pop(key)
                return
            raise ValueError(f"Goal with title: {key} not found")
        else:
            raise TypeError("Key must be an int or str")
        
    def complete_subgoal(self, key):
        if isinstance(key, int):
            self._check_index(key)
            list(self._subgoals.values())[int(key)].set_completed()
        elif isinstance(key, str):
            if (key in self._subgoals):
                self._subgoals[key].set_completed()
                return
            raise ValueError(f"Goal with title: ({key}) not found")
        else:
            raise TypeError("Key must be an int or str")

    def get_progress_fraction(self):
        return f"{self.get_completion_status()}/{self.get_num_subgoals()}"
    
    def get_progress_percent(self):
        if not self._subgoals:
            return 100.0
        return (self.get_completion_status() / self.get_num_subgoals()) * 100
