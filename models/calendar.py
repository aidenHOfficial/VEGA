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

filename = "debug.json"
def write_to_debug_file(string):
    with open(filename, 'w') as f:
        json.dump(string, f, indent=4) 

def stringify_objects(obj):
    if isinstance(obj, dict):
        return {k: stringify_objects(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [stringify_objects(v) for v in obj]
    elif isinstance(obj, tuple):
        return tuple(stringify_objects(v) for v in obj)
    elif isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    else:
        # For any other custom object
        return str(obj)

@dataclass
class Calendar:
    _time_tree: TimeTree
    _todos: List
    _dated_todos: List

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
    
    def schedule_event(self, task: Task, goal_value: float, routine_value: float, personal_value: float, relational_value: float):
        new_event = Event(task, goal_value, routine_value, personal_value, relational_value)
        
        if isinstance(task, TemporalTask):
            self._time_tree.insert(new_event)
        elif isinstance(task, Task):
            if (task._deadline):
                bisect.insort(self._dated_todos, new_event)
            else:
                self._todos.append(task)
    
    def _get_events(self, TimeInterval: TimeInterval):
        return self._time_tree.overlap_search(TimeInterval)
    
    def generate_schedule(self, date: datetime):
        domains = defaultdict(set)

        date_start = datetime(date.year, date.month, date.day)
        date_end = datetime(date.year, date.month, date.day, 23, 59, 59)
        date_time_interval = TimeInterval(date_start, date_end)
        
        arcs = self._time_tree.sweepline_overlap_search(date_time_interval)
        
        domains_json = {}
        arcs_json = {}
        constraints_json = {}
        
        # Need to update test. Currently temp_task3 have no valid domain options, causing the colapse of contraints data structure.
        
        for event in arcs:
            str_event = str(event[0])
            str_n_event = str(event[1])
            if str_event not in domains_json:
                domains_json[str_event] = []
            if str_event not in arcs_json:
                arcs_json[str_event] = {}
            if str_n_event not in arcs_json[str_event]:
                arcs_json[str_event][str_n_event] = {}
            for domain in arcs[event]:
                str_domain = str(domain[0])
                str_n_domain = str(domain[1])
                if str_domain not in arcs_json[str_event][str_n_event]:
                    arcs_json[str_event][str_n_event][str_domain] = []
                if str_n_domain not in arcs_json[str_event][str_n_event][str_domain]:
                    arcs_json[str_event][str_n_event][str_domain].append(str_n_domain)
                if str_domain not in domains_json[str_event]:
                    domains_json[str_event].append(str_domain)
                domains[event[0]].add(domain[0])
                domains[event[1]].add(domain[1])

        event_csp = CSP(domains, arcs)
        constraints = event_csp._AC3()

        for event in constraints:
            str_event = str(event)
            constraints_json[str_event] = {}
            for n_event in constraints[event]:
                str_n_event = str(n_event)
                constraints_json[str_event][str_n_event] = {}
                for d1o in constraints[event][n_event]:
                    str_d1o = str(d1o)
                    constraints_json[str_event][str_n_event][str_d1o] = []
                    for d2o in constraints[event][n_event][d1o]:
                        str_d2o = str(d2o)
                        constraints_json[str_event][str_n_event][str_d1o].append(str_d2o)
         
        debug_json = {"domains": domains_json, "arcs": arcs_json, "constraints": constraints_json} 
        print(debug_json)
        write_to_debug_file(debug_json)