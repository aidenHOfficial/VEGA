import pytest
from datetime import datetime, timedelta
from models.time_interval import TimeInterval
from models.temporal_task import TemporalTask
from models.task import Task
from models.event import Event

def test_get_priority_score_simple():
    task = Task("Make bed", "Remember after waking up to go to bed")
    temp_task = TemporalTask("Reminder", "Remind Jasmine to water her plants", datetime.now() + timedelta(0, 0, 0, 0, 5), datetime.now() + timedelta(0, 0, 0, 0, 10))

    task_event = Event(task, 10, 20, 10, 0)
    temp_task_event = Event(temp_task, 20, 15, 10, 25)

    task_event_priority = task_event.get_priority_score()
    temporal_task_event_priority = temp_task_event.get_priority_score()
        
    assert temporal_task_event_priority > task_event_priority
    
def test_get_priority_score_closer_deadline_results_in_higher_score():
    temp_task = TemporalTask("Reminder", "Test", datetime.now() + timedelta(0, 0, 0, 0, 5), datetime.now() + timedelta(0, 0, 0, 0, 10))
    temp_task_2 = TemporalTask("Reminder2", "Test2", datetime.now() + timedelta(0, 0, 0, 0, 10), datetime.now() + timedelta(0, 0, 0, 0, 15))

    temp_task_event = Event(temp_task, 20, 15, 10, 25)
    temp_task_event_2 = Event(temp_task_2, 20, 15, 10, 25)

    temporal_task_event_priority = temp_task_event.get_priority_score()
    temporal_task_event_priority_2 = temp_task_event_2.get_priority_score()

    assert temporal_task_event_priority > temporal_task_event_priority_2
        
def test_get_task():
    task = Task("Make bed", "Remember after waking up to go to bed")
    temp_task = TemporalTask("Reminder", "Remind Jasmine to water her plants", datetime.now() + timedelta(0, 0, 0, 0, 5), datetime.now() + timedelta(0, 0, 0, 0, 10))

    task_event = Event(task, 10, 20, 10, 0)
    temp_task_event = Event(temp_task, 20, 15, 10, 25)
        
    assert task_event.get_task(), task
    assert temp_task_event.get_task(), temp_task
        
def test_get_deadline():
    task = Task("Make bed", "Remember after waking up to go to bed")
    task_2 = Task("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1))

    task_event = Event(task, 10, 20, 10, 0)
    temp_task_event = Event(task_2, 20, 15, 10, 25)
        
    assert task_event.get_deadline() == None
    assert temp_task_event.get_deadline() == datetime(2025, 10, 1)
        
def test_get_startline():
    temp_task = TemporalTask("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1), datetime(2025, 10, 2))
    temp_task_2 = TemporalTask("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1), datetime(2025, 10, 2), datetime(2025, 10, 1), datetime(2025, 10, 2))
                
    temp_task_event = Event(temp_task, 20, 15, 10, 25)
    temp_task_event_2 = Event(temp_task_2, 20, 15, 10, 25)
        
    assert temp_task_event.get_startline() == None
    assert temp_task_event_2.get_startline() == datetime(2025, 10, 1)
        
def test_get_startline_invalid():
    task = Task("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1))
                
    task_event = Event(task, 20, 15, 10, 25)
        
    with pytest.raises(ValueError):
        task_event.get_startline()

def test_get_start_date():
    temp_task = TemporalTask("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1), datetime(2025, 10, 2))
                
    temp_task_event = Event(temp_task, 20, 15, 10, 25)
        
    assert temp_task_event.get_start_date() == datetime(2025, 10, 1)
        
def test_get_start_date_invalid():
    task = Task("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1))
                
    task_event = Event(task, 20, 15, 10, 25)
        
    with pytest.raises(ValueError):
        task_event.get_start_date()

def test_get_end_date():
    temp_task = TemporalTask("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1), datetime(2025, 10, 2))
                
    temp_task_event = Event(temp_task, 20, 15, 10, 25)
        
    assert temp_task_event.get_end_date() == datetime(2025, 10, 2)
        
def test_get_end_date_invalid():
    task = Task("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1))
                
    task_event = Event(task, 20, 15, 10, 25)
        
    with pytest.raises(ValueError):
        task_event.get_end_date()

def test_get_time_slot():
    temp_task = TemporalTask("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1), datetime(2025, 10, 2))
                
    temp_task_event = Event(temp_task, 20, 15, 10, 25)
        
    assert temp_task_event.get_time_slot() == TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2))
        
def test_get_time_slot_invalid():
    task = Task("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1))
                
    task_event = Event(task, 20, 15, 10, 25)
        
    with pytest.raises(ValueError):
        task_event.get_time_slot()