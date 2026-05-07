from __future__ import annotations
from typing import Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from models.task import Task
from models.time_interval import TimeInterval
from models.temporal_task import TemporalTask
from models.routine_entry import RoutineEntry

@dataclass
@Task.register
class Routine(TemporalTask):
    _repeated_time_difference = None
    _tasks = []

    def __init__(
            self,
            title: str,
            description: str,
            start_date: datetime,
            end_date: Optional[datetime] = None,
            repeated_time_difference: timedelta = timedelta(1)
        ):
        super().__init__(title, description, start_date, end_date)

        self._tasks: list[RoutineEntry] = []
        self._repeated_time_difference = repeated_time_difference

    @property
    def total_estimated_time(self):
        total = timedelta()
        for entry in self._tasks:
            total += entry.duration
        return total

    def _check_index(self, index: int):
        if index is None or index < 0 or index >= len(self._tasks):
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
        return self._tasks[key]

    def _get_routine_entry_by_title(self, key: str):
        for entry in self._tasks:
            if (entry.task._title == key):
                return entry
        raise ValueError(f"Task with title {key} not found!")

    def to_dict(self):
        return {
            **super().to_dict(),
            "_repeated_time_difference": self._repeated_time_difference.total_seconds(),
            "_tasks": [entry.to_dict() for entry in self._tasks],
        }
        
    @classmethod
    def _from_dict(cls, data):
        if data is None:
            return None
        
        obj = super()._from_dict(data)
        
        obj._repeated_time_difference = timedelta(seconds=data["_repeated_time_difference"])
        obj._tasks = [RoutineEntry.from_dict(entry) for entry in data["_tasks"]]
        
        return obj

    def get_tasks(self):
        return [entry.task for entry in self._tasks]
    
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
        self._tasks.append(RoutineEntry(task=task, duration=complete_time))

    def add_temporal_task(self, task: TemporalTask):
        complete_time = task.get_total_time()
        self._check_complete_time(complete_time)
        self._tasks.append(RoutineEntry(task=task, duration=complete_time))

    def remove_task_by_index(self, key: int):
        self._check_index(key)
        self._tasks.pop(key)

    def remove_task_by_title(self, key: str):
        for index, entry in enumerate(self._tasks):
            if (entry.task._title == key):
                self._tasks.pop(index)
                return
        raise ValueError("Task with given title not found!")

    def change_order(self, reordered_tasks: list[Task]):
        current_tasks = [entry.task for entry in self._tasks]

        if set(current_tasks) != set(reordered_tasks):
            raise ValueError("Reordered tasks must contain exactly the same tasks as before reorder!")

        task_to_entry = {entry.task: entry for entry in self._tasks}
        self._tasks = [task_to_entry[task] for task in reordered_tasks]

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
            return TimeInterval((self._start_date + self._repeated_time_difference * multiple), (self._end_date + self._repeated_time_difference * multiple))