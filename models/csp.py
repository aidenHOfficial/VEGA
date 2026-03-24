from typing import List, Dict, Set, Tuple
from datetime import timedelta
from dataclasses import dataclass
from models.time_interval import TimeInterval
from models.event import Event

@dataclass
class CSP:
    domains: Dict[Event, List[TimeInterval]]
    arcs: Dict[Tuple[Event, Event], Set[Tuple[TimeInterval, TimeInterval]]]
    constraints: Dict[Event, Dict[Event, Dict[TimeInterval, Set[TimeInterval]]]]
    assignments: Dict[Event, List[TimeInterval]]
    undo_stack: List
    solutions: List[Dict]

    def __init__(self, domains = None, arcs = None):
        self.domains = {}
        self.arcs = {}
        self.constraints = {}
        self.assignments = {}
        self.undo_stack = []
        self.solutions = []
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
        """Public function to solve the AC3 problem given the constraints

        Returns:
            List[Dict]: List of solution configurations
        """
        if not bool(self.constraints):
            self._AC3()
        self._backtrack()
        return self.solutions

    def _get_unassigned(self):
        """Returns the events which do not have an assignment in self.assignments

        Returns:
            List[Event]: The list of events without assignment
        """
        return [event for event in self.domains if event not in self.assignments]

    def _split_interval(
            self,
            intr1: TimeInterval,
            intr2: TimeInterval,
            dur1: timedelta,
            dur2: timedelta
        ):
        """ 
        This function returns 2 tuples which are the result of splitting the given intr1, intr2 
        with matching dur1, dur2 event durations. The tuples have 2 values which represent the 
        TimeInterval result of splitting its interval (intr1 / intr2) or None if there is only 1
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

        # if (intr1.start_date < intr2.start_date or (intr1.start_date == intr2.start_date and intr1.end_date < intr2.end_date)):
        #     a, b, d1 = intr1.start_date, intr1.end_date, dur1
        #     x, y, d2 = intr2.start_date, intr2.end_date, dur2
        # else:
        #     a, b, d1 = intr2.start_date, intr2.end_date, dur2
        #     x, y, d2 = intr1.start_date, intr1.end_date, dur1

        a, b, d1 = intr1.start_date, intr1.end_date, dur1
        x, y, d2 = intr2.start_date, intr2.end_date, dur2

        red = TimeInterval(a, max((y - d2), a))
        yellow = TimeInterval(min((x + d2), b), b)
        green = TimeInterval(min((a + d1), y), y)
        blue = TimeInterval(x, max((b - d1), x))

        red_valid = red.get_duration() >= d1
        yellow_valid = yellow.get_duration() >= d1
        green_valid = green.get_duration() >= d2
        blue_valid = blue.get_duration() >= d2

        if (red_valid and yellow_valid):
            res1 = red, yellow
        elif red_valid:
            res1 = red, None
        elif yellow_valid:
            res1 = yellow, None

        if (green_valid and blue_valid):
            res2 = green, blue
        elif green_valid:
            res2 = green, None
        elif blue_valid:
            res2 = blue, None

        return res1, res2

    def _undo(self, checkpoint):
        while len(self.undo_stack) > checkpoint:
            event, interval = self.undo_stack.pop()

            if interval is None:
                del self.assignments[event]
            else:
                self.assignments[event] = interval

    def _assign_split(self, event1, event2, val1, val2, checkpoint):
        self._assign(event1, val1)
        self._assign(event2, val2)
        self._backtrack()
        self._undo(checkpoint)

    def _assign(self, event, value):
        if value != self.assignments.get(event):
            # puts None using the get() function
            self.undo_stack.append((event, self.assignments.get(event)))
            self.assignments[event] = value

    def _backtrack(self):
        unassigned = self._get_unassigned()

        if len(unassigned) == 0:
            self.solutions.append(dict(self.assignments))
            return

        event = unassigned[0]

        for domain_value in self.domains[event]:
            checkpoint = len(self.undo_stack)
            self._assign(event, domain_value)

            conflict = False
            for neighbor, _ in self.constraints[event].items():
                if neighbor not in self.assignments:
                    continue
                neighbor_val = self.assignments[neighbor]
                if not domain_value.is_overlapping(neighbor_val):
                    continue

                conflict = True
                intr1, intr2 = self._split_interval(
                    domain_value, neighbor_val,
                    event.get_duration(), neighbor.get_duration()
                )

                if intr1 == (None, None) or intr2 == (None, None):
                    break

                for v1 in filter(None, intr1):
                    for v2 in filter(None, intr2):
                        split_checkpoint = len(self.undo_stack)
                        self._assign(event, v1)
                        self._assign(neighbor, v2)
                        self._backtrack()
                        self._undo(split_checkpoint)
                break

            if not conflict:
                self._backtrack()

            self._undo(checkpoint)

    # def _backtrack(self):
    #     unasigned = self._get_unassigned()

    #     if len(unasigned) == 0:
    #         self.solutions.append(self.assignments)

    #     for event in unasigned:
    #         for domain_value in self.domains[event]:
    #             self._assign(event, domain_value)
    #             for neighbor in self.constraints[event].keys():
    #                 if (neighbor in self.assignments and domain_value.is_overlapping(self.assignments[neighbor])):
    #                     neighbor_assignment = self.assignments[neighbor]
    #                     intr1, intr2 = self._split_interval(domain_value, neighbor_assignment, event.get_duration(), neighbor.get_duration())
    #                     if (intr1 == (None, None) or intr2 == (None, None)):
    #                         return
    #                     checkpoint = len(self.undo_stack)
    #                     self._assign_split(event, neighbor, intr1[0], intr2[0], checkpoint)
    #                     if (intr1[1] is not None):
    #                         if (intr2[1] is not None):
    #                             self._assign_split(event, neighbor, intr1[1], intr2[1], checkpoint)
    #                         self._assign_split(event, neighbor, intr1[1], intr2[0], checkpoint)
    #                     if (intr2[1] is not None):
    #                         self._assign_split(event, neighbor, intr1[0], intr2[1], checkpoint)

    #     unasigned = self._get_unassigned()

    #     if len(unasigned) == 0:
    #         self.solutions.append(self.assignments)