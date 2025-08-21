from __future__ import annotations
from typing import Optional, List, Dict, Tuple
from collections import defaultdict
from datetime import date, datetime, timedelta
from dataclasses import dataclass, field
import math
import bisect

# Move these somewhere else
RC = 1 # Rescheduling cost

GW = 1 # Goal weight
RW = 1 # Routine weight
PW = 1 # Personal weight
REW = 1 # Relational weight

def validate_datetime_tuple(period, label="reschedule_period"):
    if not isinstance(period, tuple) or len(period) != 2:
        raise ValueError(f"{label} must be a tuple of two datetime objects.")
    if not isinstance(period[0], datetime) or not isinstance(period[1], datetime):
        raise ValueError(f"{label} must contain datetime objects.")

@dataclass
class TimeInterval:
    start_date: datetime
    end_date: datetime
    
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        
        self.__post_init__()
        
    def __post_init__(self):
        if self.start_date > self.end_date:
            raise ValueError("start_date must be before end_date")
        
    def __eq__(self, other: TimeInterval):
        return self.start_date == other.start_date and self.end_date == other.end_date
        
    def __str__(self):
        return f"({self.start_date}, {self.end_date})"
      
    def get_start_date(self):
        return self.start_date

    def get_end_date(self):
        return self.end_date
      
    def get_interval(self):
        return (self.start_date, self.end_date)

@dataclass
class Task:
    _title: str
    _description: str
    _completed: bool = False
    _deadline: Optional[datetime] = None

    def __init__(self, title: str, description: str, deadline: Optional[datetime] = None):
        self._title = title
        self._description = description
        self._deadline = deadline

    def __eq__(self, other):
        if not isinstance(other, TemporalTask):
            return NotImplemented
        return (
            self._title == other._title and 
            self._description == other._description and
            self._completed == other._completed
        )
    
    def __hash__(self):
        return hash((self._title, self._description, self._completed))

    def get_completion_status(self):
        return self._completed
    
    def set_completed(self):
        self._completed = True
    
    def get_title(self):
        return self._title
    
    def get_description(self):
        return self._description

    def get_deadline(self):
        return self._deadline

@dataclass
class TemporalTask(Task):
    _start_date: datetime = None
    _end_date: datetime = None
    _completed = False
    _deadline: Optional[datetime] = None
    _startline: Optional[datetime] = None
    _reschedule_periods: Optional[List[TimeInterval]] = field(default_factory=list)

    def __init__(self, title: str, description: str, start_date: datetime, end_date: datetime, startline: Optional[datetime] = None, deadline: Optional[datetime] = None, reschedule_periods: Optional[List[TimeInterval]] = None):
        super().__init__(title, description, deadline)

        self._start_date = start_date
        self._end_date = end_date

        self._startline = startline

        self._reschedule_periods = reschedule_periods if reschedule_periods is not None else []

        self.__post_init__()

    def __post_init__(self):
        if self._startline and self._start_date < self._startline:
            raise ValueError("start_date must not be before startline.")
        if self._deadline and self._deadline < self._end_date:
            raise ValueError("end_date must not be after deadline.")
        if self._start_date > self._end_date:
            raise ValueError("start_date must be before end_date.")
        if (self._end_date - self._start_date) < timedelta(seconds=5):
            raise ValueError("start_date → end_date must be at least 5 seconds apart.")
        if self._startline and self._deadline and (self._deadline - self._startline) < timedelta(seconds=5):
            raise ValueError("startline → deadline must be at least 5 seconds apart.")
        for period in self._reschedule_periods:
            validate_datetime_tuple(period)
            if (self._startline and period[0] < self._startline) or (self._deadline and period[1] > self._deadline):
                raise ValueError("All reschedule periods must be within startline and deadline.")

    def __eq__(self, other):
        if not isinstance(other, TemporalTask):
            return NotImplemented
        return (
            self._title == other._title and 
            self._description == other._description and
            self._start_date == other._start_date and
            self._end_date == other._end_date and
            self._completed == other._completed
        )
    
    def __hash__(self):
        return hash((self._title, self._description, self._completed, self._start_date, self._end_date))
    
    def get_start_date(self):
        return self._start_date
    
    def get_end_date(self):
        return self._end_date

    def get_startline(self):
        return self._startline

    def get_total_time(self):
        return self._end_date - self._start_date
    
    def get_time_slot(self):
        return (self._start_date, self._end_date)

    def get_reschedule_periods(self):
        return self._reschedule_periods.copy()

    def add_reschedule_period(self, period: TimeInterval):
        if (self._startline and period.start_date < self._startline or self._deadline and period.end_date > self._deadline):
            raise ValueError("Added period must be within the period of startline, and deadline")
        self._reschedule_periods.append(period)

@dataclass
class Goal(TemporalTask):
    _subgoals: Dict[str, Task] = field(default_factory=dict)
    _completed_steps: int = 0
    
    def __init__(self, title: str, description: str, start_date: datetime, end_date: datetime, startline: Optional[datetime] = None, deadline: Optional[datetime] = None):
        super().__init__(title, description, start_date, end_date, start_date, end_date)

        self._subgoals = {}
        self._completed_steps = 0

    def __str__(self):
        return self._build_tree_str(self)

    def _build_tree_str(self, node, prefix="", is_last=True) -> str:
        connector = "└── " if is_last else "├── "
        lines = [prefix + connector + str(node.get_title())]

        new_prefix = prefix + ("    " if is_last else "│   ")
        
        if (isinstance(node, Goal)):
            child_count = len(node._subgoals)

            for i, child in enumerate(node._subgoals.values()):
                is_last_child = (i == child_count - 1)
                lines.append(self._build_tree_str(child, new_prefix, is_last_child))

        return "\n".join(lines)

    def _check_index(self, index):
        if index is None or index < 0 or index >= len(self._subgoals):
            raise IndexError("Invalid subgoal index")
    
    def _check_time_period(self, goal: Task):
        if (
            (goal.get_deadline() and goal.get_deadline() > self._deadline) or
            (
                isinstance(goal, TemporalTask) and
                (
                    (goal.get_startline() and goal.get_startline() < self._startline) or
                    (goal.get_start_date() < self._start_date) or 
                    (goal.get_end_date() > self._end_date)
                )
            )
        ):
            raise ValueError(
                "Goal can not have a start_date, end_date, startline or deadline before or past this goal's start / end"
            )
    
    def get_completion_status(self):
        completed = self._completed
        for subgoal in self._subgoals.values():
            completed += subgoal.get_completion_status()
        return int(completed)

    def get_num_subgoals(self):
        count = len(self._subgoals)
        for subgoal in self._subgoals.values():
            if (isinstance(subgoal, Goal)):
                count += subgoal.get_num_subgoals()
        return count

    def get_subgoal(self, key):
        if isinstance(key, int):
            self._check_index(key)
            values = list(self._subgoals.values())
            self._check_index(key)
            return values[key]
        elif isinstance(key, str):
            if key in self._subgoals:
                return self._subgoals[key]
            raise ValueError(f"Goal with title: {key} not found")
        raise TypeError("Key must be an int or str")
    
    def get_subgoals(self):
        return list(self._subgoals.values())

    def set_completed(self):
        for subgoal in self._subgoals.values():
            subgoal.set_completed()
        self._completed = True
    
    def add_subgoal(self, goal: Task):
        self._check_time_period(goal)

        self._subgoals[goal._title] = goal
        
        # self._check_completion()

    def remove_subgoal(self, key):
        if isinstance(key, int):
            self._check_index(key)
            del list(self._subgoals.values())[key]
        elif isinstance(key, str):
            if (key in self._subgoals):
                self._subgoals.pop(key)
                return
            raise ValueError(f"Goal with title: {key} not found")
        else:
            raise TypeError("Key must be an int or str")
        
    def complete_subgoal(self, key):
        if isinstance(key, int):
            self._check_index(key)
            list(self._subgoals.values())[int(key)].set_completed()
        elif isinstance(key, str):
            if (key in self._subgoals):
                self._subgoals[key].set_completed()
                return
            raise ValueError(f"Goal with title: ({key}) not found")
        else:
            raise TypeError("Key must be an int or str")

    def get_progress_fraction(self):
        return f"{self.get_completion_status()}/{self.get_num_subgoals()}"
    
    def get_progress_percent(self):
        if not self._subgoals:
            return 100.0
        return (self.get_completion_status() / self.get_num_subgoals()) * 100

@dataclass
class Routine(TemporalTask):
    _repeated_time_difference = None

    def __init__(self, title: str, description: str, start_date: datetime, end_date: Optional[datetime] = None, repeated_time_difference: timedelta = timedelta(1)):
        super().__init__(title, description, start_date, end_date)
        
        self._time_duration_map = {}
        self._tasks = []
        self._repeated_time_difference = repeated_time_difference

    @property
    def total_estimated_time(self):
        total = timedelta()
        for task in self._tasks:
            if isinstance(task, TemporalTask):
                total += task.get_total_time()
            else:
                total += self._time_duration_map[task]
        return total

    def _check_index(self, index):
        if index is None or index < 0 or index >= len(self._tasks):
            raise IndexError("Invalid routine index")

    def _check_complete_time(self, complete_time: timedelta):
        if (not isinstance(complete_time, timedelta)):
            raise (ValueError("Complete time provided was not a timedelta object"))
        return complete_time > timedelta(seconds=5)

    def get_tasks(self):
        return self._tasks
    
    def get_task(self, key):
        if (isinstance(key, int)):
            self._check_index(key)
            return self._tasks[key]
        elif (isinstance(key, str)):
            for task in self._tasks:
                if (task._title == key):
                    return task
            raise ValueError("Task with given title not found!")
        raise TypeError("Key must be an int or str")
    
    def get_task_complete_time(self, key):
        if (isinstance(key, int)):
            self._check_index(key)
            return self._time_duration_map[self._tasks[key]]
        elif (isinstance(key, str)):
            for item in self._tasks:
                if (item._title == key and item in self._time_duration_map):
                    return self._time_duration_map[item]
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
            self._tasks.append(task)
            self._time_duration_map[task] = complete_time
            return
        raise ValueError("Complete time must be greater than 5 seconds")

    def remove_task(self, key):
        if (isinstance(key, int)):
            self._check_index(key)
            if (self._tasks[key] in self._time_duration_map):
                self._time_duration_map.pop(self._tasks[key])

            self._tasks.pop(key)
            return
        elif (isinstance(key, str)):
            for index, task in enumerate(self._tasks):
                if (task._title == key):
                    if (key in self._time_duration_map):
                        self._time_duration_map.pop(key)
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

@dataclass
class Node:
    events: List[Event]
    max: datetime
    left: Node
    right: Node
    height: int
    
    def __init__(self, event: Event):
        self.events = [event]
        self.max = event.end_date()
        self.left = None
        self.right = None
        height = 1
        
    @property
    def event(self):
        return self.events[0]
    
    def add_event(self, event: Event):
        self.events.append(event)
        
    def get_num_events(self):
        return len(self.events)
        
    def remove_event(self, key):
        if (isinstance(key, int)):
            if (key < 0 or key > len(self.events)):
                raise IndexError("Invalid event index!")
            del self.events[key]
        elif (isinstance(key, Event)):
            self.events.remove(key)
        raise ValueError("key must be int or Event!")
        
    def get_event(self, key):
        if (isinstance(key, int)):
            if (key < 0 or key > len(self.events)):
                raise IndexError("Invalid event index!")
            return self.events[key]
        elif (isinstance(key, Event)):
            self.events.remove(key)
        raise ValueError("key must be int or Event!")
        
    def get_events(self):
        return self.events

@dataclass
class TimeTree:
    _root: Node
    
    def __init__(self):
        self._root = None
        
    def _height(self, node: Node):
        if (not node):
            return 0
        return node.height
    
    def _get_balance(self, node: Node):
        if not node:
            return 0
        return self._height(node.left) - self._height(node.right)
    
    def _min_value_node(self, node: Node):
        current = node

        while current.left is not None:
            current = current.left

        return current
    
    def _left_rotate(self, node: Node):
        child_node = node.right
        grandchild_node = child_node.left

        child_node.left = node
        node.right = grandchild_node

        node.height = 1 + max(self._height(node.left), self._height(node.right))
        child_node.height = 1 + max(self._height(child_node.left), self._height(child_node.right))

        return child_node
    
    def _right_rotate(self, node: Node):
        child_node = node.left
        grandchild_node = child_node.right

        child_node.right = node
        node.left = grandchild_node

        node.height = 1 + max(self._height(node.left), self._height(node.right))
        child_node.height = 1 + max(self._height(child_node.left), self._height(child_node.right))

        return child_node
    
    def newNode(event: Event):
        return Node(event)
    
    def insert(self, event: Event):
        return self._insert_recursive(self._root, event)
    
    def _insert_recursive(self, node: Node, event: Event):
        if node is None:
            new_node = self.newNode(event)
            if (self._root is None):
                self._root = new_node
            return new_node
        
        if (event.start_date < node.event.start_date):
            node.left = self.insert(node.left, event)
        elif (event.start_date > node.event.start_date):
            node.right = self.insert(node.right, event)
        else:
            node.add_event(event)
            return node
        
        node.height = 1 + max(self._height(node.left), self._height(node.right))

        balance = self._get_balance(node)

        if balance > 1 and event.start_date < node.left.event.start_date:
            return self._right_rotate(node)

        if balance < -1 and event.start_date > node.right.event.start_date:
            return self._left_rotate(node)

        if balance > 1 and event.start_date > node.left.event.start_date:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)

        if balance < -1 and event.start_date < node.right.event.start_date:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)
        
        if (node.max < event.end_date):
            node.max = event.end_date

        return node
    
    def delete_node(self, event: Event):
        return self._delete_node_recursive(self._root, event)
    
    def _delete_node_recursive(self, node: Node, event: Event):
        if node is None:
            return node
        
        if (event.start_date < node.event.start_date):
            node.left = self._delete_node_recursive(node.left, event)
        elif (event.start_date > node.event.start_date):
            node.right = self._delete_node_recursive(node.right, event)
        else:
            node.remove_event(event)
            
            if (node.get_num_events() == 0):
                    
                if node.left is None or node.right is None:
                    temp = node.left if node.left else node.right

                    if temp is None:
                        node = None
                    else:
                        node = temp

                else:
                    temp = self._min_value_node(node.right)
                    node.events = temp.events
                    node.right = self._delete_node_recursive(node.right, temp.key)

        if node is None:
            return node
        
        node.height = 1 + max(self._height(node.left), self._height(node.right))

        balance = self._get_balance(node)
        
        if balance > 1 and self._get_balance(node.left) >= 0:
            return self._right_rotate(node)

        if balance > 1 and self._get_balance(node.left) < 0:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)

        if balance < -1 and self._get_balance(node.right) <= 0:
            return self._left_rotate(node)

        if balance < -1 and self._get_balance(node.right) > 0:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)

        return node
    
    def _is_overlapping(event: Event, interval: TimeInterval):
        return event.start_date <= interval.start_date and interval.start_date <= event.end_date
    
    def overlap_search(self, interval: TimeInterval):
        if self._root is None:
            return None
        return self._overlap_search_recursive(self._root, interval, [])
        
    def _overlap_search_recursive(self, node: Node, interval: TimeInterval, overlaps: List):
        if self._is_overlapping(node.event, interval):
            overlaps.append(node.event)
            
        if node.left is not None and node.left.max >= interval.start_date:
            return self.overlap_search(node.left, interval)
        if node.right is not None and node.right.min <= interval.end_date:
            return self.overlap_search(node.right, interval)
        
    def inorder(self):
        return self._inorder_recursive(self._root)
        
    def _inorder_recursive(self, node: Node):
        if node is None:
            return
        
        self.inorder(node.left)
        print("[" + str(node.event.start_date) + ", " + str(node.event.end_date) + "]" + " max = " + str(node.max))
        self.inorder(node.right)

@dataclass
class Calendar:
    # Events need to be a self balancing interval tree
    _events: Dict[date, List[Event]]
    _todos: List
    _dated_todos: List

    def __init__(self):
        self._events = defaultdict(list)
        self._dated_todos = []
        self._todos = []

    def _sort_day_by_priority(self, day: date):
        self._events[day].sort(key=lambda event: event.get_priority_score(), reverse=True)

    def schedule_event(self, task: Task, goal_value: float, routine_value: float, personal_value: float, relational_value: float):
        new_event = Event(task, goal_value, routine_value, personal_value, relational_value)
        
        if isinstance(task, Task):
            if (task._deadline):
                bisect.insort(self._dated_todos, new_event)
            else:
                self._todos.append(task)
        elif isinstance(task, TemporalTask):
            event_day = task.start_date.date()
            self._events[event_day] = new_event
    
    def get_events(self, start_date: datetime, end_date: datetime):
        events = []
        for day in self._events.keys():
            if (start_date < day and day < end_date):
                events.extend(self._events[day])
        return events

    def generate_schedule(self, date: datetime):
        # CSP trying to fit everything into this. 
        # Needs to create booleans based on the available reschedule periods of each event
        
        
        # Retrieve all events for the day:
        # 
        # Enforce arc consistency
        # for event in events:
        #   if event's neighbor
        # 
        # recursive schedule function():
        #   for events in the remaining events to be scheduled:
        #       if event can be scheduled:
        #           result = rescursive_schedule_function():
        #           if result is not None:
        #               return result
        #       return None
        

        return
    

class VEGA:
    def __init__(self):
        self.goals = []
        self.routines = []
        self.callendar = Calendar()

    # bunch of managing functions

    def generate_command(self, prompt):
        return None
