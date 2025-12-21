from typing import List, Dict, Set, Tuple
from datetime import timedelta
from dataclasses import dataclass, field
from models.time_interval import TimeInterval
from models.event import Event

@dataclass
class CSP:
    domains: Dict[Event, List[TimeInterval]] = field(default_factory=dict)
    arcs: Dict[Tuple[Event, Event], Set[Tuple[TimeInterval, TimeInterval]]] = field(default_factory=dict)
    constraints: Dict[Event, Dict[Event, Dict[TimeInterval, Set[TimeInterval]]]] = field(default_factory=dict)
    assignments: Dict[Event, List[TimeInterval]] = field(default_factory=dict)
    undo_stack: List = field(default_factory=list)

    def __init__(self, domains = None, arcs = None):
        if (domains is not None):
            self.domains: Dict[Event, List[TimeInterval]] = domains
        if (arcs is not None):
            self.arcs: Dict[Tuple[Event, Event], Set[Tuple[TimeInterval, TimeInterval]]] = arcs

    def add_event(self, event: Event, intervals: List[TimeInterval]):
        self.domains[event] = intervals

    def add_arc(self, e1: Event, e2: Event, t1: TimeInterval, t2: TimeInterval):
        if (e1, e2) not in self.arcs:
            self.arcs[(e1, e2)] = set()
        self.arcs[(e1, e2)].add((t1, t2))
        
    def _time_interval_constraint(self, inter1: TimeInterval, inter2: TimeInterval, event_duration1: timedelta, event_duration2: timedelta):
        if (inter1.end_date < inter2.start_date or inter2.end_date < inter1.start_date):
            return True
        
        if (inter2.start_date <= inter1.start_date and inter1.end_date <= inter2.end_date):
            sliding_room = inter1.get_duration() - event_duration1
            left_space = (inter1.start_date - inter2.start_date) + sliding_room
            right_space = (inter2.end_date - inter1.end_date) + sliding_room
            return left_space >= event_duration2 or right_space >= event_duration2
        if (inter1.start_date <= inter2.start_date and inter2.end_date <= inter1.end_date):
            sliding_room = inter2.get_duration() - event_duration2
            left_space = (inter2.start_date - inter1.start_date) + sliding_room
            right_space = (inter1.end_date - inter2.end_date) + sliding_room
            return left_space >= event_duration1 or right_space >= event_duration1
        
        total_window = max(inter1.end_date, inter2.end_date) - min(inter1.start_date, inter2.start_date)
        if event_duration1 + event_duration2 <= total_window:
            return True
    
    def _AC3(self):
        constraints = {}
        queue = list(self.arcs.keys()).copy()
        
        while (len(queue) != 0):
            
            node, neighbor = queue.pop(0)
            
            # Can guarantee that the task for all of the nodes are temporal tasks, which have the get_duration function because
            # the generate_schedule function will only pass temporal tasks from the callendar into this function
            node_duration = node.get_duration()
            neighbor_duration = neighbor.get_duration()
            
            if node not in constraints:
                constraints[node] = {}
            if neighbor not in constraints[node]:
                constraints[node][neighbor] = {}

            if neighbor not in constraints:
                constraints[neighbor] = {}
            if node not in constraints[neighbor]:
                constraints[neighbor][node] = {}

            for d1o in self.domains[node].copy():
                for d2o in self.domains[neighbor].copy():
                    
                    if (self._time_interval_constraint(d1o, d2o, node_duration, neighbor_duration)):
                        
                        if d1o not in constraints[node][neighbor]:
                            constraints[node][neighbor][d1o] = set()
                        if d2o not in constraints[neighbor][node]:
                            constraints[neighbor][node][d2o] = set()
                        
                        constraints[node][neighbor][d1o].add(d2o)
                        constraints[neighbor][node][d2o].add(d1o)
                
                if d1o not in constraints[node][neighbor]:
                    self._revise(node, neighbor, d1o, constraints, queue)
        
        self.constraints = constraints
        return constraints

    def _revise(self, node, neighbor, bad_dom, constraints, queue):
        self.domains[node].remove(bad_dom)
        
        for check_neighbor in constraints[node]:
            if (check_neighbor == neighbor):
                continue
            
            if ((check_neighbor, node) not in queue):
                queue.append((check_neighbor, node))
            
            if bad_dom in constraints[node][check_neighbor]:
                for constraint_to_fix in constraints[node][check_neighbor][bad_dom]:
                    constraints[check_neighbor][node][constraint_to_fix].remove(bad_dom)
                    
                    if (len(constraints[check_neighbor][node][constraint_to_fix]) == 0):
                        constraints[check_neighbor][node].pop(constraint_to_fix)
                        self._revise(check_neighbor, node, constraint_to_fix, constraints, queue)
                
                constraints[node][check_neighbor].pop(bad_dom)
        
        return constraints
    
    def solve(self):
        if self.constraints is None:
            self._AC3()
        
        return self._backtrack()
    
    def _get_unassigned(self):
        for event in self.domains:
            if event not in self.assignments:
                return event
        return None
    
    def _forward_check(self, event):
        return "TODO"
    
    def mergeSplit(self, intr1: TimeInterval, intr2: TimeInterval, dur1: timedelta, dur2: timedelta):
        intr1_valid = intr1.get_duration() >= dur1
        intr2_valid = intr2.get_duration() >= dur2
        res = None

        if (intr1_valid and intr2_valid):
            res = [min(intr1.start_date, intr2.start_date), max(intr1.end_date, intr2.end_date)]
        elif (intr1_valid and not intr2_valid):
            res = intr1
        elif (not intr1_valid and intr2_valid):
            res = intr2

        return res
    
    def _split_interval(self, intr1: TimeInterval, intr2: TimeInterval, dur1: timedelta, dur2: timedelta):
        spl1 = [intr1.start_date, min(intr2.end_date - dur2, intr1.end_date)]
        spl2 = [max(intr1.start_date + dur1, intr2.start_date), intr2.end_date]
        spl3 = [intr2.start_date, min(intr1.end_date - dur1, intr2.end_date)]
        spl4 = [max(intr2.start_date + dur2, intr1.start_date), intr1.end_date]
        
        newinter1 = self.mergeSplit(spl1, spl3, dur1, dur2)
        newinter2 = self.mergeSplit(spl2, spl4, dur1, dur2)

        return newinter1, newinter2

    def _assign(self, event: Event, interval: TimeInterval):
        # Check if this interval overlaps with other assigned events
        # if so, split the intervals accordingly and push the changes to the undo stack
        # else just assign the interval to the event and push the changes to the undo stack 

        if event in self.assignments:
            return None
        
        for neighbor in self.constraints[event].keys():
            if (neighbor in self.assignments):
                intr1, intr2 = self._split_interval(interval, self.constraints[event][neighbor][interval], event.get_duration(), neighbor.get_duration())

                if (intr1 is None or intr2 is None):
                    return None # TODO
                    
    
    def _backtrack(self):
        event = self._get_unassigned()
        if (not event):
            return self.assignments
        
        for interval in self.domains[event]:
            checkpoint = len(self.undo_stack)

            self._assign(event, interval)
            if (self.forward_check(event)):
                result = self._backtrack()
                if result is not None:
                    return result
                
            self.undo(checkpoint)