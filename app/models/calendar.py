from typing import List
from collections import defaultdict
from datetime import date, datetime 
import bisect
from dataclasses import dataclass, field
from app.models.task import Task
from app.models.time_interval import TimeInterval
from app.models.temporal_task import TemporalTask
from app.models.csp import CSP
from app.models.event import Event
from app.models.time_tree import TimeTree

@dataclass
class Calendar:
    time_tree: TimeTree = field(default_factory=TimeTree)
    todos: List[Event] = field(default_factory=list)
    dated_todos: List[Event] = field(default_factory=list)
    
    def _get_day_events(self, day: date):
        return self._get_events(TimeInterval(datetime(day.year, day.month, day.day), datetime(day.year, day.month, day.day, 23, 59, 59)))

    def _get_day_events_sorted_by_priority(self, day: date):
        events = self._get_day_events(day)
        if events:
            events.sort(key=lambda event: event.get_priority_score(), reverse=True)
        return events

    def _get_events(self, TimeInterval: TimeInterval):
        return self.time_tree.overlap_search(TimeInterval)
    
    def to_dict(self):
        return {
            "time_tree": self.time_tree.to_dict(),
            "dated_todos": [event.to_dict() for event in self.dated_todos],
            "todos": [event.to_dict() for event in self.todos]
        }
        
    @classmethod
    def from_dict(cls, data):
        if data is None:
            return None
        
        obj = cls.__new__(cls)

        obj.time_tree = TimeTree.from_dict(data["time_tree"])
        obj.dated_todos = [Event.from_dict(e) for e in data["dated_todos"]]
        obj.todos = [Event.from_dict(e) for e in data["todos"]]

        return obj
    
    def schedule_event(self, task: Task, goal_value: float, routine_value: float, personal_value: float, relational_value: float):
        new_event = Event(task, goal_value, routine_value, personal_value, relational_value)
        
        if isinstance(task, TemporalTask):
            self.time_tree.insert(new_event)
        elif isinstance(task, Task):
            if (task.deadline):
                bisect.insort(self.dated_todos, new_event)
            else:
                self.todos.append(new_event)
    
    def remove_event(self, event: Event):
        self.time_tree.delete(event)

    def get_events(self, interval: TimeInterval):
        return self.time_tree.overlap_search(interval=interval)
    
    def generate_schedule(self, date: datetime):
        domains = defaultdict(set)

        date_start = datetime(date.year, date.month, date.day)
        date_end = datetime(date.year, date.month, date.day, 23, 59, 59)
        date_time_interval = TimeInterval(date_start, date_end)
        
        arcs = self.time_tree.sweepline_overlap_search(date_time_interval)

        for event, neighbor in arcs.keys():
            if event not in domains:
                domains[event] = event.schedule_intervals
            if neighbor not in domains:
                domains[neighbor] = neighbor.schedule_intervals

        event_csp = CSP(domains, arcs)

        event_csp.solve()

        return event_csp.solutions