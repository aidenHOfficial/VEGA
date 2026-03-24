from typing import List
from collections import defaultdict
from datetime import date, datetime 
import bisect
from dataclasses import dataclass
from models.task import Task
from models.time_interval import TimeInterval
from models.temporal_task import TemporalTask
from models.csp import CSP
from models.event import Event
from models.time_tree import TimeTree
import json

@dataclass
class Calendar:
    _time_tree: TimeTree
    _todos: List[Task]
    _dated_todos: List[Task]

    def __init__(self):
        self._time_tree = TimeTree()
        self._dated_todos = []
        self._todos = []

    def _get_day_events(self, day: date):
        return self._get_events(TimeInterval(datetime(day.year, day.month, day.day), datetime(day.year, day.month, day.day, 23, 59, 59)))

    def _get_day_events_sorted_by_priority(self, day: date):
        events = self._get_day_events(day)
        if events:
            events.sort(key=lambda event: event.get_priority_score(), reverse=True)
        return events

    def _get_events(self, TimeInterval: TimeInterval):
        return self._time_tree.overlap_search(TimeInterval)
    
    def to_dict(self):
        return {
            "_time_tree": self._time_tree.to_dict(),
            "_dated_todos": [event.to_dict() for event in self._dated_todos],
            "_todos": [event.to_dict() for event in self._todos]
        }
    
    def schedule_event(self, task: Task, goal_value: float, routine_value: float, personal_value: float, relational_value: float):
        new_event = Event(task, goal_value, routine_value, personal_value, relational_value)
        
        if isinstance(task, TemporalTask):
            self._time_tree.insert(new_event)
        elif isinstance(task, Task):
            if (task._deadline):
                bisect.insort(self._dated_todos, new_event)
            else:
                self._todos.append(task)
    
    def remove_event(self, event: Event):
        self._time_tree.delete(event)
    
    def generate_schedule(self, date: datetime):
        domains = defaultdict(set)

        date_start = datetime(date.year, date.month, date.day)
        date_end = datetime(date.year, date.month, date.day, 23, 59, 59)
        date_time_interval = TimeInterval(date_start, date_end)
        
        arcs = self._time_tree.sweepline_overlap_search(date_time_interval)

        for event, neighbor in arcs.keys():
            if event not in domains:
                domains[event] = event.schedule_intervals
            if neighbor not in domains:
                domains[neighbor] = neighbor.schedule_intervals

        event_csp = CSP(domains, arcs)

        event_csp.solve()

        return event_csp.solutions