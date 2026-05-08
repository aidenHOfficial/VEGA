from __future__ import annotations
from typing import Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from models.task import Task
from models.time_interval import TimeInterval

@dataclass
@Task.register
class TemporalTask(Task):
    start_date: datetime = None
    end_date: datetime = None
    startline: Optional[datetime] = None
    schedule_intervals: Optional[List[TimeInterval]] = field(default_factory=list)

    def __post_init__(self):
        #TODO: This might be incorrect. It might not always be best to merge schedule intervals.
        if (self.schedule_intervals is not None):
            for interval in self.schedule_intervals:
                self.add_schedule_interval(interval)
            self.add_schedule_interval(TimeInterval(self.start_date, self.end_date))

        if self.startline and self.start_date < self.startline:
            raise ValueError("start_date must not be before startline.")

        if self.deadline and self.deadline < self.end_date:
            raise ValueError("end_date must not be after deadline.")

        if self.start_date > self.end_date:
            raise ValueError("start_date must be before end_date.")

        if (self.end_date - self.start_date) < timedelta(seconds=5):
            raise ValueError("start_date → end_date must be at least 5 seconds apart.")

        if self.startline and self.deadline and (self.deadline - self.startline) < timedelta(seconds=5):
            raise ValueError("startline → deadline must be at least 5 seconds apart.")

        for interval in self.schedule_intervals:
            if (
                (self.startline and interval.start_date < self.startline) or 
                (self.deadline and interval.end_date > self.deadline)
            ):
                raise ValueError("All reschedule periods must be within startline and deadline.")

    def __hash__(self):
        return hash((self.title, self.description, self.completed, self.start_date, self.end_date, self.deadline))
    
    def to_dict(self):
        return {
            **super().to_dict(),
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "startline": self.startline.isoformat() if self.startline is not None else None,
            "completed": self.completed,
            "schedule_intervals": [interval.to_dict() for interval in self.schedule_intervals]
        }
        
    @classmethod
    def _from_dict(cls, data):
        obj = super()._from_dict(data)

        obj.start_date = datetime.fromisoformat(data["start_date"])
        obj.end_date = datetime.fromisoformat(data["end_date"])
        obj.startline = (
            datetime.fromisoformat(data["startline"])
            if data["startline"] else None
        )
        obj.schedule_intervals = [
            TimeInterval.from_dict(i) for i in data["schedule_intervals"]
        ]

        return obj

    def get_start_date(self):
        return self.start_date

    def get_end_date(self):
        return self.end_date

    def get_startline(self):
        return self.startline

    def get_total_time(self):
        return self.end_date - self.start_date

    def get_time_slot(self):
        return TimeInterval(self.start_date, self.end_date)

    def get_schedule_intervals(self):
        return self.schedule_intervals.copy()

    def get_duration(self):
        return self.end_date - self.start_date 

    def add_schedule_interval(self, interval: TimeInterval):
        if (
            (self.startline and interval.start_date < self.startline) or 
            (self.deadline and interval.end_date > self.deadline) 
        ):            
            raise ValueError("Added period must be within the interval of [start_date, end_date] and [start_line, end_line]")
        
        merge_intervals = [] 
        for s_interval in self.schedule_intervals:
            if (s_interval.is_overlapping(interval)):
                merge_intervals.append(s_interval) 

        merged_interval = interval
        for merger in merge_intervals:
            self.schedule_intervals.remove(merger)
            merged_interval = TimeInterval(
                min(merged_interval.start_date, merger.start_date),
                max(merged_interval.end_date, merger.end_date)
            )

        self.schedule_intervals.append(merged_interval)