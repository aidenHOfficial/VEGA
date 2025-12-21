from __future__ import annotations
from datetime import datetime
from dataclasses import dataclass

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
    
    def __hash__(self):
        return hash(self.__str__())
      
    def get_start_date(self):
        return self.start_date

    def get_end_date(self):
        return self.end_date
      
    def get_interval(self):
        return (self.start_date, self.end_date)
    
    def get_duration(self):
        return self.end_date - self.start_date

    def is_overlapping(self, interval: TimeInterval):
        return self.start_date <= interval.end_date and interval.start_date <= self.end_date