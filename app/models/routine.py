from __future__ import annotations
from datetime import timedelta
from dataclasses import dataclass, field
from typing import List
from app.models.task import Task
from app.models.time_interval import TimeInterval
from app.models.temporal_task import TemporalTask
from app.models.routine_entry import RoutineEntry

@dataclass
@Task.register
class Routine(TemporalTask):
    repeated_time_difference: timedelta = timedelta(0)
    tasks: List[RoutineEntry] = field(default_factory=list)

    @property
    def total_estimated_time(self):
        total = timedelta()
        for entry in self.tasks:
            total += entry.duration
        return total

    def _check_index(self, index: int):
        if index is None or index < 0 or index >= len(self.tasks):
            raise IndexError("Invalid routine index")

    def _check_complete_time(self, complete_time: timedelta):
        if complete_time is None:
            raise ValueError("Complete time can not be none")
        if not isinstance(complete_time, timedelta):
            raise ValueError("Complete time provided was not a timedelta object")
        if complete_time < timedelta(seconds=5):
            raise ValueError("Complete time must be greater than 5 seconds")
        if complete_time > self.get_total_time():
            raise ValueError("Complete time must be less than the complete time of routine")

    def _get_routine_entry_by_index(self, key: int):
        self._check_index(key)
        return self.tasks[key]

    def _get_routine_entry_by_title(self, key: str):
        for entry in self.tasks:
            if (entry.task.title == key):
                return entry
        raise ValueError(f"Task with title {key} not found!")

    def to_dict(self):
        return {
            **super().to_dict(),
            "repeated_time_difference": self.repeated_time_difference.total_seconds(),
            "tasks": [entry.to_dict() for entry in self.tasks],
        }
        
    @classmethod
    def _from_dict(cls, data):
        if data is None:
            return None
        
        obj = super()._from_dict(data)
        
        obj.repeated_time_difference = timedelta(seconds=data["repeated_time_difference"])
        obj.tasks = [RoutineEntry.from_dict(entry) for entry in data["tasks"]]
        
        return obj

    def get_tasks(self):
        return [entry.task for entry in self.tasks]
    
    def get_task_by_index(self, key: int):
        return self._get_routine_entry_by_index(key).task

    def get_task_by_title(self, key: str):
        return self._get_routine_entry_by_title(key).task

    def get_task_complete_time_by_index(self, key: int):
        return self._get_routine_entry_by_index(key).duration

    def get_task_complete_time_by_title(self, key: str):
        return self._get_routine_entry_by_title(key).duration

    def get_estimated_time(self):
        return self.total_estimated_time

    def add_task(self, task: Task, complete_time: timedelta):
        self._check_complete_time(complete_time)
        self.tasks.append(RoutineEntry(task=task, duration=complete_time))

    def add_temporal_task(self, task: TemporalTask):
        complete_time = task.get_total_time()
        self._check_complete_time(complete_time)
        self.tasks.append(RoutineEntry(task=task, duration=complete_time))

    def remove_task_by_index(self, key: int):
        self._check_index(key)
        self.tasks.pop(key)

    def remove_task_by_title(self, key: str):
        for index, entry in enumerate(self.tasks):
            if (entry.task.title == key):
                self.tasks.pop(index)
                return
        raise ValueError("Task with given title not found!")

    def change_order(self, reordered_tasks: list[Task]):
        current_tasks = [entry.task for entry in self.tasks]

        if set(current_tasks) != set(reordered_tasks):
            raise ValueError("Reordered tasks must contain exactly the same tasks as before reorder!")

        task_to_entry = {entry.task: entry for entry in self.tasks}
        self.tasks = [task_to_entry[task] for task in reordered_tasks]

    def change_task_complete_time_by_index(self, key: int, complete_time: timedelta):
        self._check_complete_time(complete_time)
        entry = self._get_routine_entry_by_index(key)
        entry.duration = complete_time

    def change_task_complete_time_by_title(self, key: str, complete_time: timedelta):
        self._check_complete_time(complete_time)
        entry = self._get_routine_entry_by_title(key)
        entry.duration = complete_time

    def get_next_time_slot(self, multiple: int):
        if (multiple < 1):
            raise ValueError("Multiple not greater than 1")
        if (self._start_date is not None and self._end_date is not None):
            return TimeInterval((self._start_date + self.repeated_time_difference * multiple), (self._end_date + self.repeated_time_difference * multiple))