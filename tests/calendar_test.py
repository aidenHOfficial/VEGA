import pytest
from datetime import datetime
from models.time_interval import TimeInterval
from models.temporal_task import TemporalTask
from models.task import Task
from models.calendar import Calendar 
from models.event import Event

def test_generate_schedule():
    cal = Calendar()

    temp_task = TemporalTask("A", "A", start_date=datetime(2025, 10, 2, 1), end_date=datetime(2025, 10, 2, 2), startline=None, deadline=None, schedule_intervals=[TimeInterval(datetime(2025, 10, 2, 4), datetime(2025, 10, 2, 5))])
    cal.schedule_event(temp_task, 20, 15, 10, 25)

    temp_task2 = TemporalTask("B", "B", start_date=datetime(2025, 10, 2, 3), end_date=datetime(2025, 10, 2, 5), startline=None, deadline=None, schedule_intervals=[TimeInterval(datetime(2025, 10, 2, 5), datetime(2025, 10, 2, 6))])
    cal.schedule_event(temp_task2, 20, 15, 10, 25)

    temp_task3 = TemporalTask("C", "C", start_date=datetime(2025, 10, 2, 5), end_date=datetime(2025, 10, 2, 8), startline=None, deadline=None, schedule_intervals=[TimeInterval(datetime(2025, 10, 2, 3), datetime(2025, 10, 2, 5))])
    cal.schedule_event(temp_task3, 20, 15, 10, 25)

    res = cal.generate_schedule(datetime(2025, 10, 2))
    assert res is not None

    cal = Calendar()

    temp_task = TemporalTask("A", "A", start_date=datetime(2025, 10, 2, 0), end_date=datetime(2025, 10, 2, 4), startline=None, deadline=None, schedule_intervals=[TimeInterval(datetime(2025, 10, 2, 3), datetime(2025, 10, 2, 9))])
    cal.schedule_event(temp_task, 20, 15, 10, 25)

    temp_task2 = TemporalTask("B", "B", start_date=datetime(2025, 10, 2, 1), end_date=datetime(2025, 10, 2, 3), startline=None, deadline=None, schedule_intervals=[TimeInterval(datetime(2025, 10, 2, 3), datetime(2025, 10, 2, 5))])
    cal.schedule_event(temp_task2, 20, 15, 10, 25)

    temp_task3 = TemporalTask("C", "C", start_date=datetime(2025, 10, 2, 7), end_date=datetime(2025, 10, 2, 9), startline=None, deadline=None, schedule_intervals=[TimeInterval(datetime(2025, 10, 2, 9), datetime(2025, 10, 2, 10))])
    cal.schedule_event(temp_task3, 20, 15, 10, 25)

    res = cal.generate_schedule(datetime(2025, 10, 2))
    assert res is not None

def test_add_event():
    calendar = Calendar()
        
    temp_task = TemporalTask("Test", "Example text", start_date=datetime(2025, 10, 1), end_date=datetime(2025, 10, 2))
    calendar.schedule_event(temp_task, 20, 15, 10, 25)

    event = Event(temp_task, 20, 15, 10, 25)
    cal_event = calendar._get_events(TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))[0].event

    assert event == cal_event

def test_remove_event():
    calendar = Calendar()
        
    temp_task = TemporalTask("Test", "Example text", start_date=datetime(2025, 10, 1), end_date=datetime(2025, 10, 2))
    task_event = Event(temp_task, 20, 15, 10, 25)
    calendar.schedule_event(task_event, 20, 20, 20, 20)

    calendar.remove_event(task_event)

    assert calendar._get_events(TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2))) == []

def test_remove_event_invalid():
    calendar = Calendar()
        
    temp_task = TemporalTask("Test", "Example text", start_date=datetime(2025, 10, 1), end_date=datetime(2025, 10, 2))
    temp_task2 = Task("Test", "Example text")
    calendar.schedule_event(temp_task, 20, 20, 20, 20)

    temp_event = calendar._get_events(TimeInterval(datetime(2025, 9, 30), datetime(2025, 10, 3)))[0].event
    temp_event2 = Event(temp_task2, 20, 20, 20, 20)
    calendar.remove_event(temp_event)

    assert calendar.remove_event(temp_event) is None
    with pytest.raises(ValueError):
        calendar.remove_event(temp_event2)

def test_get_events():
    calendar = Calendar()

    temp_task = TemporalTask("Test", "Example text", start_date=datetime(2025, 10, 1), end_date=datetime(2025, 10, 2))
    task_event = Event(temp_task, 20, 15, 10, 25)
    calendar.schedule_event(temp_task, 20, 15, 10, 25)

    assert task_event == calendar._get_events(TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))[0].event
    
def test_to_dict():
    calendar = Calendar()

    task = Task("Test", "Example text")
    dated_task = Task("Test2", "Example text", deadline=datetime(2025, 10, 1))
    temp_task = TemporalTask("Test3", "Example text", start_date=datetime(2025, 10, 1), end_date=datetime(2025, 10, 2))
    calendar.schedule_event(temp_task, 20, 15, 10, 25)
    calendar.schedule_event(task, 20, 15, 10, 25)
    calendar.schedule_event(dated_task, 20, 15, 10, 25)
    
    expected = {'time_tree': {'size': 1, 'root': {'key': {'start_date': '2025-10-01T00:00:00', 'end_date': '2025-10-02T00:00:00'}, 'min': '2025-10-01T00:00:00', 'max': '2025-10-02T00:00:00', 'height': 1, 'events': [{'task': {'type': 'TemporalTask', 'title': 'Test3', 'description': 'Example text', 'completed': False, 'deadline': None, 'start_date': '2025-10-01T00:00:00', 'end_date': '2025-10-02T00:00:00', 'startline': None, 'schedule_intervals': [{'start_date': '2025-10-01T00:00:00', 'end_date': '2025-10-02T00:00:00'}]}, 'goal_value': 20, 'routine_value': 15, 'personal_value': 10, 'relational_value': 25}], 'left': None, 'right': None}}, 'dated_todos': [{'task': {'type': 'Task', 'title': 'Test2', 'description': 'Example text', 'completed': False, 'deadline': '2025-10-01T00:00:00'}, 'goal_value': 20, 'routine_value': 15, 'personal_value': 10, 'relational_value': 25}], 'todos': [{'task': {'type': 'Task', 'title': 'Test', 'description': 'Example text', 'completed': False, 'deadline': None}, 'goal_value': 20, 'routine_value': 15, 'personal_value': 10, 'relational_value': 25}]}

    assert calendar.to_dict() == expected

def test_from_dict():
    json = {'time_tree': {'size': 1, 'root': {'key': {'start_date': '2025-10-01T00:00:00', 'end_date': '2025-10-02T00:00:00'}, 'min': '2025-10-01T00:00:00', 'max': '2025-10-02T00:00:00', 'height': 1, 'events': [{'task': {'type': 'TemporalTask', 'title': 'Test3', 'description': 'Example text', 'completed': False, 'deadline': None, 'start_date': '2025-10-01T00:00:00', 'end_date': '2025-10-02T00:00:00', 'startline': None, 'schedule_intervals': [{'start_date': '2025-10-01T00:00:00', 'end_date': '2025-10-02T00:00:00'}]}, 'goal_value': 20, 'routine_value': 15, 'personal_value': 10, 'relational_value': 25}], 'left': None, 'right': None}}, 'dated_todos': [{'task': {'type': 'Task', 'title': 'Test2', 'description': 'Example text', 'completed': False, 'deadline': '2025-10-01T00:00:00'}, 'goal_value': 20, 'routine_value': 15, 'personal_value': 10, 'relational_value': 25}], 'todos': [{'task': {'type': 'Task', 'title': 'Test', 'description': 'Example text', 'completed': False, 'deadline': None}, 'goal_value': 20, 'routine_value': 15, 'personal_value': 10, 'relational_value': 25}]}
    calendar = Calendar.from_dict(json)

    task = Task("Test", "Example text")
    dated_task = Task("Test2", "Example text", deadline=datetime(2025, 10, 1))
    temp_task = TemporalTask("Test3", "Example text", start_date=datetime(2025, 10, 1), end_date=datetime(2025, 10, 2))
    expected = Calendar()
    expected.schedule_event(temp_task, 20, 15, 10, 25)
    expected.schedule_event(task, 20, 15, 10, 25)
    expected.schedule_event(dated_task, 20, 15, 10, 25)

    assert calendar == expected