from __future__ import annotations
from typing import Optional, List, Dict, Tuple
from collections import defaultdict
from datetime import date, datetime, timedelta
from dataclasses import dataclass, field
import math
import bisect
from collections import deque
from collections import deque

# Move these somewhere else
RC = 1 # Rescheduling cost

GW = 1 # Goal weight
RW = 1 # Routine weight
PW = 1 # Personal weight
REW = 1 # Relational weight

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
    
    def __lt__(self, other):
        if not isinstance(other, TimeInterval):
            return NotImplemented
        return (self.start_date, self.end_date) < (other.start_date, other.end_date)

    def __str__(self):
        return f"({self.start_date}, {self.end_date})"
      
    def get_start_date(self):
        return self.start_date

    def get_end_date(self):
        return self.end_date
      
    def get_interval(self):
        return (self.start_date, self.end_date)

    def is_overlapping(self, interval: TimeInterval):
        return self.start_date <= interval.end_date and interval.start_date <= self.end_date

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
    _schedule_intervals: Optional[List[TimeInterval]] = None

    def __init__(self, title: str, description: str, start_date: datetime, end_date: datetime, startline: Optional[datetime] = None, deadline: Optional[datetime] = None, schedule_intervals: Optional[List[TimeInterval]] = None):
        super().__init__(title, description, deadline)

        self._start_date = start_date
        self._end_date = end_date

        self._startline = startline

        schedule_intervals = schedule_intervals or []

        schedule_intervals.append(TimeInterval(start_date, end_date))

        self._schedule_intervals = schedule_intervals.copy()

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
        for interval in self._schedule_intervals:
            if (
                (self._startline and interval.start_date < self._startline) or 
                (self._deadline and interval.end_date > self._deadline) or 
                (interval.start_date < self._start_date) or
                (interval.end_date < self._end_date) 
            ):
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
        return TimeInterval(self._start_date, self._end_date)

    def get_schedule_intervals(self):
        return self._schedule_intervals.copy()

    def add_schedule_interval(self, interval: TimeInterval):
        if (
            (self._startline and interval.start_date < self._startline) or 
            (self._deadline and interval.end_date > self._deadline) or 
            (interval.start_date < self._start_date) or
            (interval.end_date < self._end_date) 
        ):            
            raise ValueError("Added period must be within the interval of [start_date, end_date] and [start_line, end_line]")
        
        merge_intervals = [] 
        for s_interval in self._schedule_intervals:
            if (s_interval.is_overlapping(interval)):
                merge_intervals.append(s_interval) 

        merged_interval = interval
        for merger in merge_intervals:
            self._schedule_intervals.remove(merger)
            merged_interval = TimeInterval(min(merged_interval.start_date, merger.start_date), max(merged_interval.end_date, merger.end_date)) 
        
        self._schedule_intervals.append(merged_interval)

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

    def __eq__(self, other):
        if not isinstance(other, Event):
            return NotImplemented
        return self._task == other._task and self._goal_value == other._goal_value and self._routine_value == other._routine_value and self._personal_value == other._personal_value and self._relational_value == other._relational_value

    def __str__(self):
        return f"Event(Task: {self._task.get_title()}, goal_value: {self._goal_value}, routine_value: {self._routine_value}, personal_value: {self._personal_value}, relational_value: {self._relational_value})"

    def __hash__(self):
        return hash(self.__str__())

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

@dataclass
class Node:
    events: List[Event]
    key: TimeInterval
    max: datetime
    min: datetime
    left: Node
    right: Node
    height: int
    
    def __init__(self, event: Event, key: TimeInterval):
        self.events = [event]
        self.max = key.end_date
        self.min = key.start_date
        self.left = None
        self.right = None
        self.height = 1
        self.key = key
    
    def add_event(self, event: Event):
        if (event.get_time_slot() != self.key):
            raise ValueError("Event time slot does not match node time slot!")
        self.events.append(event)
        
    def get_num_events(self):
        return len(self.events)
        
    def remove_event(self, key):
        if (isinstance(key, int)):
            if (key < 0 or key > len(self.events)):
                raise IndexError("Invalid event index!")
            del self.events[key]
            return
        if (isinstance(key, str)):
            for index, event in enumerate(self.events):
                if (event._task._title == key):
                    del self.events[index]
                    return
            raise ValueError("Event with given title not found!")
        elif (isinstance(key, Event)):
            self.events.remove(key)
            return
        raise TypeError("key must be string int or Event!")
        
    def get_event(self, key):
        if (isinstance(key, int)):
            if (key < 0 or key > len(self.events)):
                raise IndexError("Invalid event index!")
            return self.events[key]
        if (isinstance(key, str)):
            for event in self.events:
                if (event._task._title == key):
                    return event
            raise ValueError("Event with given title not found!")
        raise TypeError("key must be int or string!")
        
    def get_events(self):
        return self.events
    
    def get_key(self):
        return self.key

@dataclass
class TimeTree:  
    _root: Node
    _size: int
    
    def __init__(self):
        self._root = None
        self._size = 0
        
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

        node.max = max(
            node.key.end_date,
            node.left.max if node.left else datetime.min,
            node.right.max if node.right else datetime.min
        )
        child_node.max = max(
            child_node.key.end_date,
            child_node.left.max if child_node.left else datetime.min,
            child_node.right.max if child_node.right else datetime.min
        )

        return child_node
    
    def _right_rotate(self, node: Node):
        child_node = node.left
        grandchild_node = child_node.right

        child_node.right = node
        node.left = grandchild_node

        node.height = 1 + max(self._height(node.left), self._height(node.right))
        child_node.height = 1 + max(self._height(child_node.left), self._height(child_node.right))

        node.max = max(
            node.key.end_date,
            node.left.max if node.left else datetime.min,
            node.right.max if node.right else datetime.min
        )
        child_node.max = max(
            child_node.key.end_date,
            child_node.left.max if child_node.left else datetime.min,
            child_node.right.max if child_node.right else datetime.min
        )

        return child_node
    
    def _insert_recursive(self, node: Node, event: Event, key: TimeInterval):
        if node is None:
            new_node = self._new_node(event, key)
            if (self._root is None):
                self._root = new_node
            self._size += 1
            return new_node
        
        if (key < node.key):
            node.left = self._insert_recursive(node.left, event, key)
        elif (key > node.key):
            node.right = self._insert_recursive(node.right, event, key)
        else:
            node.add_event(event)
            return node
        
        node.height = 1 + max(self._height(node.left), self._height(node.right))

        left_max = node.left.max if node.left else datetime.min
        right_max = node.right.max if node.right else datetime.min
        node.max = max(node.key.end_date, left_max, right_max)

        balance = self._get_balance(node)

        if balance > 1 and key < node.left.key:
            return self._right_rotate(node)

        if balance < -1 and key > node.right.key:
            return self._left_rotate(node)

        if balance > 1 and key > node.left.key:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)

        if balance < -1 and key < node.right.key:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)

        return node
    
    def _delete_node_recursive(self, node: Node, event: Event, key: TimeInterval):
        if node is None:
            return node
        
        if (key < node.key):
            node.left = self._delete_node_recursive(node.left, event, key)
        elif (key > node.key):
            node.right = self._delete_node_recursive(node.right, event, key)
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
                    node.key = temp.key
                    node.events = temp.events
                    node.right = self._delete_node_recursive(node.right, event, temp.key)
                
                self._size -= 1

        if node is None:
            return node
        
        node.height = 1 + max(self._height(node.left), self._height(node.right))

        left_max = node.left.max if node.left else datetime.min
        right_max = node.right.max if node.right else datetime.min
        node.max = max(node.key.end_date, left_max, right_max)

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

    def _new_node(self, event: Event, key: TimeInterval):
        return Node(event, key)
    
    def _is_overlapping(self, interval1: TimeInterval, interval2: TimeInterval):
        return interval1.start_date <= interval2.end_date and interval2.start_date <= interval1.end_date

    def _overlap_search_recursive(self, node: Node, interval: TimeInterval, overlaps: List):
        if node.key.is_overlapping(interval):
            overlaps.extend(node.get_events())
            
        if node.left is not None and node.left.max >= interval.start_date:
            self._overlap_search_recursive(node.left, interval, overlaps)
        if node.right is not None and node.right.min <= interval.end_date:
            self._overlap_search_recursive(node.right, interval, overlaps)

    def _inorder_recursive(self, node: Node):
        if node is None:
            return
        
        self._inorder_recursive(node.left)
        print("[" + str(node.key.start_date) + ", " + str(node.key.end_date) + "]" + " max = " + str(node.max))
        self._inorder_recursive(node.right)

    def _print_tree_recursive(self, node: Node, prefix: str, is_left: bool):
        if node is not None:
            print(prefix + ("├── " if is_left else "└── ") + str(node.key) + f" ({node.get_num_events()} events) " + ("Left Node" if is_left else "Right Node"))
            self._print_tree_recursive(node.left, prefix + ("│   " if is_left else "    "), True)
            self._print_tree_recursive(node.right, prefix + ("│   " if is_left else "    "), False)

    def get_size(self):
        return self._size

    def insert(self, event: Event):
        if (not isinstance(event.get_task(), TemporalTask)):
            raise ValueError("Event task must be a TemporalTask to be inserted into TimeTree")
        for time_interval in event.get_task().get_schedule_intervals():
            self._root = self._insert_recursive(self._root, event, time_interval)

    def delete(self, event: Event):
        if (not isinstance(event.get_task(), TemporalTask)):
            raise ValueError("The only events in the tree are those with TemporalTask tasks")
        for time_interval in event.get_task().get_schedule_intervals():
            self._root = self._delete_node_recursive(self._root, event, time_interval)

    def search(self, key: TimeInterval):
        current = self._root
        while current is not None:
            if key == current.key:
                return current
            elif key < current.key:
                current = current.left
            else:
                current = current.right
        raise ValueError("Key not found in tree")

    def overlap_search(self, interval: TimeInterval):
        if self._root is None:
            return None
        overlaps = []
        self._overlap_search_recursive(self._root, interval, overlaps)

        return overlaps
    
    def sweepline_overlap_search(self, interval: TimeInterval):
        """Generates a mapping of all overlapping events within the given interval using the sweep line algorithm.

        Args:
            interval (TimeInterval): The time interval to search for overlapping events.

        Returns:
            dict: A dictionary mapping each event to a list of events that overlap with it.
        """

        if self._root is None:
            return None
        overlapping_blocks = []
        self._overlap_search_recursive(self._root, interval, overlapping_blocks)

        sweep_line_points = []
        for block in overlapping_blocks:
            sweep_line_points.append({"time": block.start_date, "liminal": "start", "event": block.event})
            sweep_line_points.append({"time": block.end_date, "liminal": "end", "event": block.event})
        sweep_line_points.sort(key=lambda e: (e["time"], 0 if e["liminal"] == "start" else 1))

        overlaps = {}
        active_points = []
        for point in sweep_line_points:
            if point[1] == "start":
                for active_point in active_points:
                    overlaps[point["event"]] = active_point
                    overlaps[active_point] = point["event"]
            
                active_points.append([point["event"]])

            elif point["liminal"] == "end":
                del active_points[point["event"]]

        return overlaps
    
    def inorder(self):
        return self._inorder_recursive(self._root)

    def print_tree(self):
        self._print_tree_recursive(self._root, "", True)

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
    
    def _AC3(domains, arcs, constraint):
        queue = []
        constraints = {}
        for arc in arcs:
            queue.append(arc)
        while (len(queue) != 0):
            node, n_node = queue.pop(0)
            for d1o in domains[node]:
                for d2o in domains[n_node]:
                    if (constraint(d1o, d2o)):
                        constraint[arc][d1o].append(d2o)
            
    def schedule_event(self, task: Task, goal_value: float, routine_value: float, personal_value: float, relational_value: float):
        new_event = Event(task, goal_value, routine_value, personal_value, relational_value)
        
        if isinstance(task, TemporalTask):
            self._time_tree.insert(new_event)
        elif isinstance(task, Task):
            if (task._deadline):
                bisect.insort(self._dated_todos, new_event)
            else:
                self._todos.append(task)
    
    def get_events(self, TimeInterval: TimeInterval):
        return self._time_tree.overlap_search(TimeInterval)
    
    def generate_schedule(self, date: datetime):
        blocks = self._get_day_events(date.date())
        blocks.sort(key=lambda b: (b.start_date, b.end_date))

        constraints = {}
        domains = {}
        neighbors = {}

        date_start = datetime(date.year, date.month, date.day)
        date_end = datetime(date.year, date.month, date.day, 23, 59, 59)
        date_time_interval = TimeInterval(date_start, date_end)
       
        arcs = self._time_tree.sweepline_overlap_search(date_time_interval)

        self.AC3(list(domains.keys()), domains, neighbors, constraints)
        
        return

class VEGA:
    def __init__(self):
        self.goals = []
        self.routines = []
        self.callendar = Calendar()

    # bunch of managing functions

    def generate_command(self, prompt):
        return None