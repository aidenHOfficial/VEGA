from __future__ import annotations
from typing import List
from datetime import datetime
from dataclasses import dataclass
from models.event import Event
from models.time_interval import TimeInterval

@dataclass
class TimeTreeNode:
    events: List[Event]
    key: TimeInterval
    max: datetime
    min: datetime
    left: TimeTreeNode
    right: TimeTreeNode
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