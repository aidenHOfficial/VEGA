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
    task: Task
    goal_value: float
    routine_value: float
    personal_value: float
    relational_value: float
        
    def __post_init__(self):
        check_list = [self.goal_value, self.routine_value, self.personal_value, self.relational_value]
        
        for value in check_list:
            if (value < 0 or value > 100 / len(check_list)):
                raise ValueError(f"{value} can not be less than 0, or greater than {100 / len(check_list)}")

    def __hash__(self):
        return hash((hash(self.task), self.goal_value, self.routine_value, self.personal_value, self.relational_value))
    
    def __repr__(self):
        return f"Event(title:{self.task.title}, description:{self.task.description})"

    def _time_difference_to_now(self):

        if isinstance(self.task, TemporalTask):
            scheduled_time = self.task.get_end_date()
        elif (self.task.get_deadline() is not None):
            scheduled_time = self.task.get_deadline()
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
        # m * ((math.e**((time_diffrerence / d) + shift) - math.e**(-((time_diffrerence / d) + shift))) / (math.e**((time_diffrerence / d) + shift) + math.e**(-((time_diffrerence / d) + shift)))) + m
        temp1 = (time_diffrerence / d) + shift
        temp2 = (math.e ** temp1 - math.e ** (-temp1))
        temp3 = (math.e ** temp1 + math.e ** (-temp1))
        score = (m * (temp2 / temp3)) + m
        return score

    def _get_scemantic_score(self):
        # Returns a score between 0 and 100
        return min((GW * self.goal_value) + (RW * self.routine_value) + (PW * self.personal_value) + (REW * self.relational_value), 100)

    @property
    def schedule_intervals(self):
        if (isinstance(self.task, TemporalTask)):
            return self.task.get_schedule_intervals()
        return None

    @property
    def start_date(self):
        if (isinstance(self.task, TemporalTask)):
            return self.task.get_start_date()
        return None

    @property
    def end_date(self):
        if (isinstance(self.task, TemporalTask)):
            return self.task.get_end_date()
        return None

    @property
    def startline(self):
        if (isinstance(self.task, TemporalTask)):
            return self.task.get_startline()
        return None

    @property
    def deadline(self):
        return self.task.get_deadline()
    
    def to_dict(self):
        return {
            "task": self.task.to_dict(),
            "goal_value": self.goal_value,
            "routine_value": self.routine_value,
            "personal_value": self.personal_value,
            "relational_value": self.relational_value
        }
        
    @classmethod
    def from_dict(cls, data):
        if data is None:
            return None
        
        obj = cls.__new__(cls)

        obj.task = Task.from_dict(data["task"])
        obj.goal_value = int(data["goal_value"])
        obj.routine_value = int(data["routine_value"])
        obj.personal_value = int(data["personal_value"])
        obj.relational_value = int(data["relational_value"])

        return obj
        
    def get_priority_score(self):
        return self._get_scemantic_score() * self._get_urgency_score()
    
    def get_task(self):
        return self.task
    
    def get_deadline(self):
        return self.task.deadline
    
    def get_startline(self):
        if (isinstance(self.task, TemporalTask)):
            return self.task.get_startline()
        raise ValueError("Event task is not a Temporal Task, and has no start line!")
    
    def get_start_date(self):
        if (isinstance(self.task, TemporalTask)):
            return self.task.get_start_date()
        raise ValueError("Event task is not a Temporal Task, and has no start date!")

    def get_end_date(self):
        if (isinstance(self.task, TemporalTask)):
            return self.task.get_end_date()
        raise ValueError("Event task is not a Temporal Task, and has no end date!")
    
    def get_time_slot(self):
        if (isinstance(self.task, TemporalTask)):
            return self.task.get_time_slot()
        raise ValueError("Event task is not a Temporal Task, and has no time slot!")
    
    def get_duration(self):
        if (isinstance(self.task, TemporalTask)):
            return self.task.get_duration()
        raise ValueError("Event task is not a Temporal Task, and has no duration!")