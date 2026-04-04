from __future__ import annotations
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from models.task import Task
from models.temporal_task import TemporalTask

@dataclass
class RoutineEntry:
    task: TemporalTask
    duration: timedelta

    def to_dict(self):
        return {
            "task": self.task,
            "duration": self.duration.isoformat()
        }

@dataclass
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
            task = entry["task"]
            if isinstance(task, TemporalTask):
                total += task.get_total_time()
            else:
                total += entry["duration"]
        return total

    def _check_index(self, index):
        if index is None or index < 0 or index >= len(self._tasks):
            raise IndexError("Invalid routine index")

    def _check_complete_time(self, complete_time: timedelta):
        if (not isinstance(complete_time, timedelta)):
            raise (ValueError("Complete time provided was not a timedelta object"))
        return complete_time > timedelta(seconds=5)

    def to_dict(self):
        return {
           "_repeated_time_difference": self._repeated_time_difference,
           "_tasks": [entry.to_dict() for entry in self._tasks],
        }

    def get_tasks(self):
        return self._tasks
    
    def get_task(self, key):
        if (isinstance(key, int)):
            self._check_index(key)
            return self._tasks[key]
        elif (isinstance(key, str)):
            for entry in self._tasks:
                if (entry.task._title == key):
                    return entry.task
            raise ValueError("Task with given title not found!")
        raise TypeError("Key must be an int or str")
    
    def get_task_complete_time(self, key):
        if (isinstance(key, int)):
            self._check_index(key)
            return self._tasks[key].duration
        elif (isinstance(key, str)):
            for entry in self._tasks:
                if (entry.task._title == key):
                    return entry.duration
            raise ValueError("Task with given title not found!")
        raise TypeError("Key must be an int or str")
    
    def get_estimated_time(self):
        return self.total_estimated_time

    def add_task(self, task: Task, complete_time: Optional[timedelta] = None):
        if complete_time is None:
            if (isinstance(task, TemporalTask)):
                if task.get_total_time() is None or task.get_total_time() > self.get_total_time():
                    raise ValueError("complete_time must be less than the complete time of routine")
                complete_time = task.get_total_time()
            else:
                raise ValueError("A complete time must be provided to add a task. Either add start / end date of temporal task, or complete_time of non-temporal task")
        if self._check_complete_time(complete_time):
            self._tasks.append(
                RoutineEntry(task=task, duration=complete_time)
            )
            return
        raise ValueError("Complete time must be greater than 5 seconds")

    def remove_task(self, key):
        if (isinstance(key, int)):
            self._tasks.pop(key)
            return
        elif (isinstance(key, str)):
            for index, entry in enumerate(self._tasks):
                if (entry.task._title == key):
                    self._tasks.pop(index)
                    return
            raise ValueError("Task with given title not found!")
        raise TypeError("Key must be an int or str")

    def change_order(self, reordered_tasks: list):
        if set(self._tasks) != set(reordered_tasks):
            raise ValueError("Reordered tasks must contain exactly the same tasks as before reorder!")
        self._tasks = reordered_tasks

    def change_task_complete_time(self, key, complete_time: timedelta):
        task = None
        if isinstance(key, int):
            self._check_index(key)
            task = self._tasks[key]
        elif isinstance(key, str):
            for current_task in self._tasks:
                if (current_task._title == key):
                    task = current_task
            if (not task):
                raise ValueError("Task with given title not found!")
        else:
            raise TypeError("Key must be an int or str")
                    

        if isinstance(task, TemporalTask):
            raise ValueError("Cannot set complete_time directly for TemporalTask. Change its start / end date instead.")
        if complete_time is None:
            raise ValueError("Complete_time can not be none")

        if self._check_complete_time(complete_time):
            self._time_duration_map[task] = complete_time

    def get_next_time_slot(self, multiple: int):
        if (multiple < 1):
            raise ValueError("Multiple not greater than 1")
        if (self._start_date is not None and self._end_date is not None):
            return (self._start_date + self._repeated_time_difference * multiple), (self._end_date + self._repeated_time_difference * multiple)