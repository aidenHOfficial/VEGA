import pytest
from datetime import datetime
from models.time_interval import TimeInterval
from models.temporal_task import TemporalTask
from models.task import Task
from models.calendar import Calendar 
from models.event import Event

def test_generate_schedule():
    cal = Calendar()

    temp_task = TemporalTask("A", "A", datetime(2025, 10, 2, 1), datetime(2025, 10, 2, 2), None, None, [TimeInterval(datetime(2025, 10, 2, 4), datetime(2025, 10, 2, 5))])
    cal.schedule_event(temp_task, 20, 15, 10, 25)

    temp_task2 = TemporalTask("B", "B", datetime(2025, 10, 2, 3), datetime(2025, 10, 2, 5), None, None, [TimeInterval(datetime(2025, 10, 2, 5), datetime(2025, 10, 2, 6))])
    cal.schedule_event(temp_task2, 20, 15, 10, 25)

    temp_task3 = TemporalTask("C", "C", datetime(2025, 10, 2, 5), datetime(2025, 10, 2, 8), None, None, [TimeInterval(datetime(2025, 10, 2, 3), datetime(2025, 10, 2, 5))])
    cal.schedule_event(temp_task3, 20, 15, 10, 25)

    res = cal.generate_schedule(datetime(2025, 10, 2))
    assert res is not None

    cal = Calendar()

    temp_task = TemporalTask("A", "A", datetime(2025, 10, 2, 0), datetime(2025, 10, 2, 4), None, None, [TimeInterval(datetime(2025, 10, 2, 3), datetime(2025, 10, 2, 9))])
    cal.schedule_event(temp_task, 20, 15, 10, 25)

    temp_task2 = TemporalTask("B", "B", datetime(2025, 10, 2, 1), datetime(2025, 10, 2, 3), None, None, [TimeInterval(datetime(2025, 10, 2, 3), datetime(2025, 10, 2, 5))])
    cal.schedule_event(temp_task2, 20, 15, 10, 25)

    temp_task3 = TemporalTask("C", "C", datetime(2025, 10, 2, 7), datetime(2025, 10, 2, 9), None, None, [TimeInterval(datetime(2025, 10, 2, 9), datetime(2025, 10, 2, 10))])
    cal.schedule_event(temp_task3, 20, 15, 10, 25)

    res = cal.generate_schedule(datetime(2025, 10, 2))
    assert res is not None

def test_add_event():
    calendar = Calendar()
        
    temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
    calendar.schedule_event(temp_task, 20, 15, 10, 25)

    event = Event(temp_task, 20, 15, 10, 25)
    cal_event = calendar._get_events(TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))[0]["event"]

    assert event == cal_event

def test_remove_event():
    calendar = Calendar()
        
    temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
    task_event = Event(temp_task, 20, 15, 10, 25)
    calendar.schedule_event(task_event, 20, 20, 20, 20)

    calendar.remove_event(task_event)

    assert calendar._get_events(TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2))) is None

def test_remove_event_invalid():
    calendar = Calendar()
        
    temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
    temp_task2 = Task("Test", "Example text")
    calendar.schedule_event(temp_task, 20, 20, 20, 20)

    temp_event = calendar._get_events(TimeInterval(datetime(2025, 9, 30), datetime(2025, 10, 3)))[0]["event"]
    temp_event2 = Event(temp_task2, 20, 20, 20, 20)
    calendar.remove_event(temp_event)

    assert calendar.remove_event(temp_event) is None
    with pytest.raises(ValueError):
        calendar.remove_event(temp_event2)

def test_get_events():
    calendar = Calendar()

    temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
    task_event = Event(temp_task, 20, 15, 10, 25)
    calendar.schedule_event(temp_task, 20, 15, 10, 25)

    assert task_event == calendar._get_events(TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))[0]["event"]
    
def test_to_dict():
    calendar = Calendar()

    task = Task("Test", "Example text")
    dated_task = Task("Test2", "Example text", datetime(2025, 10, 1))
    temp_task = TemporalTask("Test3", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
    calendar.schedule_event(temp_task, 20, 15, 10, 25)
    calendar.schedule_event(task, 20, 15, 10, 25)
    calendar.schedule_event(dated_task, 20, 15, 10, 25)
    
    print(calendar.to_dict())
    expected = {'_time_tree': {'_size': 1, '_nodes': {'key': {'start_date': '2025-10-01T00:00:00', 'end_date': '2025-10-02T00:00:00'}, 'min': '2025-10-01T00:00:00', 'max': '2025-10-02T00:00:00', 'height': 1, 'events': [{'_task': {'_type': 'TemporalTask', '_title': 'Test3', '_description': 'Example text', '_completed': False, '_deadline': None, '_start_date': '2025-10-01T00:00:00', '_end_date': '2025-10-02T00:00:00', '_startline': None, '_schedule_intervals': [{'start_date': '2025-10-01T00:00:00', 'end_date': '2025-10-02T00:00:00'}]}, '_goal_value': 20, '_routine_value': 15, '_personal_value': 10, '_relational_value': 25}], 'left': None, 'right': None}}, '_dated_todos': [{'_task': {'_type': 'Task', '_title': 'Test2', '_description': 'Example text', '_completed': False, '_deadline': '2025-10-01T00:00:00'}, '_goal_value': 20, '_routine_value': 15, '_personal_value': 10, '_relational_value': 25}], '_todos': [{'_type': 'Task', '_title': 'Test', '_description': 'Example text', '_completed': False, '_deadline': None}]}
    
    assert calendar.to_dict() == expected