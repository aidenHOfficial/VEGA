from __future__ import annotations
from typing import Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from models.task import Task
from models.time_interval import TimeInterval

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
        self._schedule_intervals = []
        
        if (schedule_intervals is not None):
            for interval in schedule_intervals:
                self.add_schedule_interval(interval)
        self.add_schedule_interval(TimeInterval(start_date, end_date))

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
                (self._deadline and interval.end_date > self._deadline)
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
            self._startline == other._startline and
            self._deadline == other._deadline and
            self._completed == other._completed
        )
    
    def __str__(self):
        return f"TemporalTask(\n\tTitle: {self._title}\n\tDescription: {self._description}\n\tStart Date: {self._start_date}\n\tEnd Date: {self._end_date}\n\tStart Line: {self._startline}\n\tDead Line: {self._deadline}\n\tCompleted: {self._completed}\n)"
    
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
    
    def get_duration(self):
        return self._end_date - self._start_date 

    def add_schedule_interval(self, interval: TimeInterval):
        if (
            (self._startline and interval.start_date < self._startline) or 
            (self._deadline and interval.end_date > self._deadline) 
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