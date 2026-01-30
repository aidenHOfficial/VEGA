from typing import List, Dict, Set, Tuple
from datetime import timedelta
from dataclasses import dataclass
from models.time_interval import TimeInterval
from models.event import Event
from enum import Enum

@dataclass
class CSP:
    domains: Dict[Event, List[TimeInterval]] 
    arcs: Dict[Tuple[Event, Event], Set[Tuple[TimeInterval, TimeInterval]]] 
    constraints: Dict[Event, Dict[Event, Dict[TimeInterval, Set[TimeInterval]]]] 
    assignments: Dict[Event, List[TimeInterval]] 
    undo_stack: List 
    class UndoAction(Enum):
        DOMAIN = 1
        ASSIGNMENT = 2

    def __init__(self, domains = None, arcs = None):
        self.domains = {}
        self.arcs = {}
        self.constraints = {}
        self.assignments = {}
        self.undo_stack = []
        if (domains is not None):
            self.domains = domains
        if (arcs is not None):
            self.arcs = arcs

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
        return [event for event in self.domains if event not in self.assignments]
    
    def _split_interval(self, intr1: TimeInterval, intr2: TimeInterval, dur1: timedelta, dur2: timedelta):
        """ 
        This function returns 2 tuples which are the result of splitting the given intr1, intr2 with matching dur1, dur2 event durations.
        The tuples have 2 values which represent the TimeInterval result of splitting its interval (intr1 / intr2) or None if there is only 1
        valid TimeInterval result for the split.


        Args:
            intr1 (TimeInterval): The first interval of time to be split
            intr2 (TimeInterval): The second interval of time to be split 
            dur1 (timedelta): The event duration for the first interval
            dur2 (timedelta): The event duration for the second interval

        Returns:
            ((TimeInterval?, TimeInterval?), (TimeInterval?, TimeInterval?))
        """
        res1 = None, None
        res2 = None, None

        if (intr1.start_date < intr2.start_date):
            a, b, d1 = intr1.start_date, intr1.end_date, dur1 
            x, y, d2 = intr2.start_date, intr2.end_date, dur2
        else:
            a, b, d1 = intr2.start_date, intr2.end_date, dur2
            x, y, d2 = intr1.start_date, intr1.end_date, dur1

        red = TimeInterval(a, (y - d2))
        yellow = TimeInterval((x + d2), b)
        green = TimeInterval((a + d1), y)
        blue = TimeInterval(x, (b - d1))

        red_valid = red.get_duration() >= d1
        yellow_valid = yellow.get_duration() >= d1
        green_valid = green.get_duration() >= d2
        blue_valid = blue.get_duration() >= d2

        if (red_valid and yellow_valid):
            if (red.is_overlapping(yellow)):
                res1 = TimeInterval(min(red.start_date, yellow.start_date), max(red.end_date, yellow.end_date)), None
            res1 = red, yellow
        elif (red_valid):
            res1 = red, None
        elif (yellow_valid):
            res1 = yellow, None

        if (green_valid and blue_valid):
            if (green.is_overlapping(blue)):
                res2 = TimeInterval(min(green.start_date, blue.start_date), max(green.end_date, blue.end_date)), None
            res2 = green, blue
        elif (green_valid):
            res2 = green, None
        elif (blue_valid):
            res2 = blue, None

        return res1, res2

    def _assign(self, event: Event, interval: TimeInterval):
        self.assignments[event] = interval

        for neighbor in self.constraints[event].keys():

            if (neighbor in self.assignments and interval.is_overlapping(self.assignments[neighbor])):
                neighbor_interval = self.assignments[neighbor]
                intr1, intr2 = self._split_interval(interval, neighbor_interval, event.get_duration(), neighbor.get_duration())

                if (intr1 == (None, None) or intr2 == (None, None)):
                    return False

                if (neighbor_interval != intr2):
                    if (intr2[1] is not None):
                        self.undo_stack.append((neighbor, intr1[1]))
                    self.undo_stack.append((neighbor, neighbor_interval))
                    self.assignments[neighbor] = intr2

                if (self.assignments[event] != intr1):
                    self.assignments[event] = intr1

        self.undo_stack.append((event, None))
        return True
    
    def _undo(self, checkpoint):
        while (len(self.undo_stack) > checkpoint):
            action, event, interval = self.undo_stack.pop()

            if (action == 1): # DOMAIN update
                undo_list = self.domains
            else:
                undo_list = self.assignments

            if (interval is None):
                del undo_list[event]
            else:
                undo_list[event] = interval
    
    def _backtrack(self):
        unasigned_events = self._get_unassigned()
        if (len(unasigned_events) == 0):
            return True
        for event in unasigned_events:
            for sched_intrvl in self.domains[event].copy(): # This might be wrong not sure
                checkpoint = len(self.undo_stack)
                if (self._assign(event, sched_intrvl) and self._backtrack()):
                    return True
                self._undo(checkpoint)
        return False