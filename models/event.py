from __future__ import annotations
from datetime import datetime, timedelta
import math
from dataclasses import dataclass
from models.task import Task
from models.temporal_task import TemporalTask

RC = 1 # Rescheduling cost

GW = 1 # Goal weight
RW = 1 # Routine weight
PW = 1 # Personal weight
REW = 1 # Relational weight

@dataclass
class Event:
    _task: Task
    _goal_value: float
    _routine_value: float
    _personal_value: float
    _relational_value: float
    
    def __init__(self, task: Task, goal_value: float, routine_value: float, personal_value: float, relational_value: float):
        self._task = task
        self._goal_value = goal_value
        self._routine_value = routine_value
        self._personal_value = personal_value
        self._relational_value = relational_value
        
        self.__post_init__()
        
    def __post_init__(self):
        check_list = [self._goal_value, self._routine_value, self._personal_value, self._relational_value]
        
        for value in check_list:
            if (value < 0 or value > 100 / len(check_list)):
                raise ValueError(f"{value} can not be less than 0, or greater than {100 / len(check_list)}")

    def __eq__(self, other):
        if not isinstance(other, Event):
            return NotImplemented
        return self._task == other._task and self._goal_value == other._goal_value and self._routine_value == other._routine_value and self._personal_value == other._personal_value and self._relational_value == other._relational_value

    def __str__(self):
        return f"Event(Task: {self._task.get_title()}, goal_value: {self._goal_value}, routine_value: {self._routine_value}, personal_value: {self._personal_value}, relational_value: {self._relational_value})"

    def __hash__(self):
        return hash(self.__str__())
    
    def __repr__(self):
        return f"Event(title:{self._task._title}, description:{self._task._description})"

    def _time_difference_to_now(self):

        if isinstance(self._task, TemporalTask):
            scheduled_time = self._task.get_end_date()
        elif (self._task.get_deadline() is not None):
            scheduled_time = self._task.get_deadline()
        else:
            return timedelta(0)

        return datetime.now() - scheduled_time
    
    def _get_urgency_score(self):
        # Returns a score between 0 and 100

        shift = 1.09861228867
        d = 23.44065
        m = 50

        time_diffrerence = self._time_difference_to_now().total_seconds() / 3600

        # m * tanh((t/d)+s) + m
        return m * ((math.e**((time_diffrerence / d) + shift) - math.e**(-((time_diffrerence / d) + shift))) / (math.e**((time_diffrerence / d) + shift) + math.e**(-((time_diffrerence / d) + shift)))) + m

    def _get_scemantic_score(self):
        # Returns a score between 0 and 100

        return min((GW * self._goal_value) + (RW * self._routine_value) + (PW * self._personal_value) + (REW * self._relational_value), 100)
    
    @property
    def schedule_intervals(self):
        if (isinstance(self._task, TemporalTask)):
            return self._task.get_schedule_intervals()
        return None
    
    @property
    def start_date(self):
        if (isinstance(self._task, TemporalTask)):
            return self._task.get_start_date()
        return None
        
    @property
    def end_date(self):
        if (isinstance(self._task, TemporalTask)):
            return self._task.get_end_date()
        return None
    
    @property
    def startline(self):
        if (isinstance(self._task, TemporalTask)):
            return self._task.get_startline()
        return None
        
    @property
    def deadline(self):
        return self._task.get_deadline()
    
    def get_priority_score(self):
        return self._get_scemantic_score() * self._get_urgency_score()
    
    def get_task(self):
        return self._task
    
    def get_deadline(self):
        return self._task._deadline
    
    def get_startline(self):
        if (isinstance(self._task, TemporalTask)):
            return self._task.get_startline()
        raise ValueError("Event task is not a Temporal Task, and has no start line!")
    
    def get_start_date(self):
        if (isinstance(self._task, TemporalTask)):
            return self._task.get_start_date()
        raise ValueError("Event task is not a Temporal Task, and has no start date!")

    def get_end_date(self):
        if (isinstance(self._task, TemporalTask)):
            return self._task.get_end_date()
        raise ValueError("Event task is not a Temporal Task, and has no end date!")
    
    def get_time_slot(self):
        if (isinstance(self._task, TemporalTask)):
            return self._task.get_time_slot()
        raise ValueError("Event task is not a Temporal Task, and has no time slot!")
    
    def get_duration(self):
        if (isinstance(self._task, TemporalTask)):
            return self._task.get_duration()
        raise ValueError("Event task is not a Temporal Task, and has no duration!")
