from datetime import datetime
import os, json
from enum import Enum
from typing import List, Optional

from models.calendar import Calendar
from models.task import Task
from models.temporal_task import TemporalTask
from models.time_interval import TimeInterval

class Controller():
    LOCAL_SAVE_LOCATION: str = "..\saves\calendar.json"
    DEFAULT_GOAL_VALUE = 20
    DEFAULT_ROUTINE_VALUE = 20
    DEFAULT_PERSONAL_VALUE = 20
    DEFAULT_RELATIONAL_VALUE = 20
    class TaskTypes(Enum):
        TASK = 1
        TEMPORALTASK = 2

    def __init__(self):
        self._load_calendar()

    def _save_calendar(self):
        data = self.calendar.to_dict()
        
        with open(self.LOCAL_SAVE_LOCATION, "w") as f:
            json.dump(data, f, sort_keys=True, indent=4)

    def _load_calendar(self):
        loc = self.LOCAL_SAVE_LOCATION

        if (not os.path.isfile(loc)):
            self.calendar = Calendar()
            self._save_calendar()
            return

        with open(loc, 'r') as f:
            data = json.loads(f)
            self.calendar = Calendar.from_dict(data)
    
    def schedule_task(
            self, 
            title: str, 
            description: str, 
            deadline: datetime = None):
        
        #TODO: Predict goal, routine, personal, relational value
        
        task = Task(title, description, deadline)
        self.calendar.schedule_event(
            task=task, 
            goal_value=self.DEFAULT_GOAL_VALUE, 
            routine_value=self.DEFAULT_ROUTINE_VALUE, 
            personal_value=self.DEFAULT_PERSONAL_VALUE, 
            relational_value=self.DEFAULT_RELATIONAL_VALUE)

    def schedule_temporal_task(
            self, 
            title: str, 
            description: str, 
            start_date: datetime,
            end_date: datetime,
            startline: datetime = None,
            deadline: datetime = None,
            schedule_intervals: Optional[List[TimeInterval]] = None):
        
        #TODO: Predict goal, routine, personal, relational value
        
        task = TemporalTask(
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            startline=startline,
            deadline=deadline,
            schedule_intervals=schedule_intervals
        )
        self.calendar.schedule_event(
            task=task, 
            goal_value=self.DEFAULT_GOAL_VALUE, 
            routine_value=self.DEFAULT_ROUTINE_VALUE, 
            personal_value=self.DEFAULT_PERSONAL_VALUE, 
            relational_value=self.DEFAULT_RELATIONAL_VALUE)
