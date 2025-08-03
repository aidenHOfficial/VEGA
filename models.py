from __future__ import annotations
from typing import Optional, List, Dict, Tuple
from collections import defaultdict
from datetime import date, datetime, timedelta
from dataclasses import dataclass, field
import math

# Move these somewhere else
RC = 1 # Rescheduling cost

GW = 1 # Goal weight
RW = 1 # Routine weight
PW = 1 # Personal weight
RW = 1 # Relational weight

def validate_datetime_tuple(period, label="reschedule_period"):
    if not isinstance(period, tuple) or len(period) != 2:
        raise ValueError(f"{label} must be a tuple of two datetime objects.")
    if not isinstance(period[0], datetime) or not isinstance(period[1], datetime):
        raise ValueError(f"{label} must contain datetime objects.")

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
    _reschedule_periods: Optional[List[Tuple[datetime, datetime]]] = field(default_factory=list)

    def __init__(self, title: str, description: str, start_date: datetime, end_date: datetime, startline: Optional[datetime] = None, deadline: Optional[datetime] = None, reschedule_periods: Optional[List[Tuple[datetime, datetime]]] = None):
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
        for period in self._reschedule_periods:
            validate_datetime_tuple(period)
            if (self._startline and period[0] < self._startline) or (self._deadline and period[1] > self._deadline):
                raise ValueError("All reschedule periods must be within startline and deadline.")

    def get_start_date(self):
        return self._start_date
    
    def get_end_date(self):
        return self._end_date

    def get_start_line(self):
        return self._startline

    def get_total_time(self):
        return self._end_date - self._start_date
    
    def get_time_slot(self):
        return (self._start_date, self._end_date)

    def get_reschedule_periods(self):
        return self._reschedule_periods.copy()

    def add_reschedule_period(self, period: Tuple[datetime, datetime]):
        if (self._startline  and period[0] < self._startline or self._deadline and period[1] > self._deadline):
            raise ValueError("Added period must be within the period of startline, and deadline")
        self._reschedule_periods.append(period)

@dataclass
class Goal(TemporalTask):
    _start_date: datetime = None
    _end_date: datetime = None
    _completed = False
    _deadline: Optional[datetime] = None
    _startline: Optional[datetime] = None
    _subgoals: Optional[Dict[ Goal]] = field(default_factory=list)
    _completed_steps: int = 0
    
    def __init__(self, title: str, description: str, start_date: datetime, end_date: datetime, startline: Optional[datetime] = None, deadline: Optional[datetime] = None):
        super().__init__(title, description, start_date, end_date, start_date, end_date)

        self._subgoals = []
        self._completed_steps = 0

    def __str__(self):
        return self._build_tree_str(self)

    def _build_tree_str(self, node, prefix="", is_last=True) -> str:
        connector = "└── " if is_last else "├── "
        lines = [prefix + connector + str(node.get_title())]

        new_prefix = prefix + ("    " if is_last else "│   ")
        child_count = len(node._subgoals)

        for i, child in enumerate(node._subgoals):
            is_last_child = (i == child_count - 1)
            lines.append(self._build_tree_str(child, new_prefix, is_last_child))

        return "\n".join(lines)

    def _check_index(self, index):
        if index is None or index < 0 or index >= len(self._subgoals):
            raise IndexError("Invalid subgoal index")
    
    def _check_end_date(self, goal: Task):
        if ((goal.get_deadline() and goal.get_deadline() > self._deadline) or 
            (isinstance(goal, TemporalTask) and 
                (goal.get_start_date() < self._start_date) or 
                (goal.get_end_date() > self._end_date) or 
                (goal.get_start_line() and goal.get_start_line() < self._startline))):
            raise ValueError("Goal can not have a start_date, end_date, startline or deadline before or past this goal's start / end")
        return

    def _check_completion(self):
        self._completed_steps = self.get_completion_status()

        if (self._completed_steps == len(self._subgoals) - 1):
            self.completed = True
        else:
            self.completed = False
        
        return self._completed_steps

    def get_completion_status(self):
        completed = int(self._completed)
        for subgoal in self._subgoals:
            completed += subgoal.get_completion_status()
        return completed

    def get_num_subgoals(self):
        count = len(self._subgoals)
        for subgoal in self._subgoals:
            count += subgoal.get_num_subgoals()
        return count

    def get_subgoal(self, index: int):
        self._check_index(index)

        return self._subgoals[index]

    def get_next_subgoal(self):
        for subgoal in self._subgoals:
            if (subgoal.complete == False):
                return subgoal
        return None

    def set_completed(self):
        for subgoal in self._subgoals:
            subgoal.set_completed()
        self._completed = True
    
    def add_subgoal(self, goal: Task):
        self._check_end_date(goal)

        self._subgoals.append(goal)
        
        self._subgoals.sort(key=lambda x: getattr(x, 'start_date', datetime.min))

        self._check_completion()

    def remove_subgoal(self, index: int):
        self._check_index(index)

        del self._subgoals[index]

        self._check_completion()
        
    def complete_subgoal(self, index: int):
        self._check_index(index)

        self._subgoals[index].set_completed()

        self._check_completion()

    def get_progress_fraction(self):
        self._check_completion()

        return f"{self._completed_steps}/{len(self._subgoals)}"
    
    def get_progress_percent(self):
        self._check_completion()

        if not self._subgoals:
            return 100.0
        return (self._completed_steps / len(self._subgoals)) * 100

class Routine(TemporalTask):

    def __init__(self, title: str, description: str, start_date: datetime, end_date: Optional[datetime] = None, repeated_time_difference: timedelta = timedelta(1)):
        super().__init__(title, description, start_date, end_date)

        self.repeated_time_difference = repeated_time_difference
        self.time_duration_map = {}

        self.tasks = []

    @property
    def total_estimated_time(self):
        total = timedelta()
        for task in self.tasks:
            if isinstance(task, TemporalTask):
                total += task.get_total_time()
            else:
                total += self.time_duration_map[task]
        return total

    def _check_index(self, index):
        if index is None or index < 0 or index >= len(self.subgoals):
            raise IndexError("Invalid subgoal index")

    def check_complete_time(self, timedelta: timedelta):
        return timedelta > timedelta(0, 5, 0, 0, 0, 0, 0)

    def get_tasks(self):
        return self.tasks
    
    def get_task(self, index: int):
        self._check_index(index)

        return self.tasks[index]
    
    def get_estimated_time(self):
        return self.total_estimated_time

    def add_task(self, task: Task, complete_time: Optional[timedelta] = None):
        if complete_time is None:
            if isinstance(task, TemporalTask) and task.get_total_time() is not None:
                complete_time = task.get_total_time()
            else:
                raise ValueError("A complete time must be provided to add a task. Either add start / end date of temporal task, or complete_time of non-temporal task")

        if self.check_complete_time(complete_time):
            self.tasks.append(task)
            self.tasks.sort(key=lambda x: getattr(x, 'start_date', datetime.min))

            if isinstance(task, Task):
                self.time_duration_map[task] = complete_time

    def remove_task(self, index: int):
        self._check_index(index)

        if (self.tasks[index] in self.time_duration_map):
            self.time_duration_map.pop(self.tasks[index])

        self.tasks.pop(index)

    def change_order(self, reordered_tasks: list):
        if set(self.tasks) != set(reordered_tasks):
            raise Exception("Reordered tasks must contain exactly the same tasks as before reorder!")
        self.tasks = reordered_tasks

    def change_task_complete_time(self, index: int, complete_time: timedelta):
        self._check_index(index)
        task = self.tasks[index]

        if isinstance(task, TemporalTask):
            raise ValueError("Cannot set complete_time directly for TemporalTask. Change its start / end date instead.")
        if complete_time is None:
            raise ValueError("Complete_time can not be none")

        if self.check_complete_time(complete_time):
            self.time_duration_map[task] = complete_time

    def get_next_time_slot(self, multiple: int):
        if (multiple < 1):
            raise ValueError("Multiple not greater than 1")
        if (self.start_date is not None and self.end_date is not None):
            return (self.start_date + self.repeated_time_difference * multiple), (self.end_date + self.repeated_time_difference)
        return None

class Event:
    
    def __init__(self, task: TemporalTask, goal_value: float, routine_value: float, personal_value: float, relational_value: float):
        self.task = task
        self.goal_value = goal_value
        self.routine_value = routine_value
        self.personal_value = personal_value
        self.relational_value = relational_value

    def time_difference_to_now(self):

        if isinstance(self.task, TemporalTask):
            if (self.task.get_deadline() is not None):
                scheduled_time = self.task.get_deadline()
            else:
                scheduled_time = self.task.get_end_date()

        return scheduled_time - datetime.now()
    
    def get_urgency_score(self):
        # Returns a score between 0 and 100

        shift = 1.09861228867
        d = 23.44065
        m = 50

        time_diffrerence = self.time_difference_to_now().hours()

        # m * tanh((t/d)+s) + m
        return m * ((math.e**((time_diffrerence / d) + shift) - math.e**(-((time_diffrerence / d) + shift))) / (math.e**((time_diffrerence / d) + shift) + math.e**(-((time_diffrerence / d) + shift)))) + m

    def get_scemantic_score(self):
        # Returns a score between 0 and 100

        return max((GW * self.goal_value) + (RW * self.routine_value) + (PW * self.personal_value) + (RW * self.relational_value), 100)
    
    def get_priority_score(self):
        return self.get_priority_score() * self.get_urgency_score()
    
class Calendar:

    def __init__(self):
        self.events: Dict[date, List[Event]] = defaultdict(list) #Event objects that hold Task and Temporal Task objects  

    def schedule_event(self, task: TemporalTask, goal_value: float, routine_value: float, personal_value: float, relational_value: float):
        new_event = Event(task, goal_value, routine_value, personal_value, relational_value)
        event_day = task.start_date.date()
        self.events[event_day] = new_event
    
    def get_events(self, start_date: datetime, end_date: datetime):
        events = []
        for day in self.events.keys():
            if (start_date < day and day < end_date):
                events.extend(self.events[day])
        return events

    def generate_schedule(self, date: datetime):
        return
    
    def sort_day_by_priority(self, day: date):
        self.events[day].sort(key=lambda event: event.get_priority_score(), reverse=True)
















    # def schedule_event(self, event: Event):
    #     task = event.task

    #     if isinstance(task, Routine):
    #         self._schedule_routine(event)
    #     elif isinstance(task, Goal) or isinstance(task, TemporalTask):
    #         self._schedule_temporal_task(event)
    #     elif isinstance(task, Task):
    #         self._schedule_flexible_task(event)

    # def _schedule_routine(self, event: Event):
    #     task = event.task
    #     repetition = task.start_date
    #     while repetition <= task.end_date:
    #         day = repetition.date()
    #         self.daily_schedule[day].append(event)
    #         repetition += task.repeated_time_difference

    # def _schedule_temporal_task(self, event: Event):
    #     task = event.task
    #     current = task.start_date.date()
    #     end = task.end_date.date()
    #     while current <= end:
    #         self.daily_schedule[current].append(event)
    #         current += timedelta(days=1)

    # def _schedule_flexible_task(self, event: Event):
    #     task = event.task
    #     # Try to place it in a day before its deadline if specified
    #     today = date.today()
    #     last_day = today + task.deadline if task.deadline else today + timedelta(days=30)
    #     current = today
    #     while current <= last_day:
    #         self.daily_schedule[current].append(event)
    #         break  # Place it once and stop

    # def _sort_day_by_priority(self, day: date):
    #     self.daily_schedule[day].sort(key=lambda event: event.get_priority_score(), reverse=True)
    
    # def get_schedule_for_day(self, day: date) -> List[Event]:
    #     return self.daily_schedule.get(day, [])

class VEGA:
    def __init__(self):
        self.goals = []
        self.routines = []
        self.callendar = Calendar()

    # bunch of managing functions

    def generate_command(self, prompt):
        return None
