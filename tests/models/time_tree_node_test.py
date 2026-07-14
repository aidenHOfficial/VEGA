import pytest
from datetime import datetime
from app.models.time_interval import TimeInterval
from app.models.temporal_task import TemporalTask
from app.models.time_tree_node import TimeTreeNode
from app.models.event import Event

def test_add_event():
    temp_task = TemporalTask("Test", "Example text", start_date=datetime(2025, 10, 1), end_date=datetime(2025, 10, 2))
    task_event = Event(temp_task, 20, 15, 10, 25)
    node = TimeTreeNode(task_event, TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))
        
    temp_task2 = TemporalTask("Make bed", "Remember after waking up to go to bed", start_date=datetime(2025, 10, 1), end_date=datetime(2025, 10, 2))
    temp_task3 = TemporalTask("Reminder", "Remind Jasmine to water her plants", start_date=datetime(2025, 10, 1), end_date=datetime(2025, 10, 2))

    task_event2 = Event(temp_task2, 10, 20, 10, 0)
    task_event3 = Event(temp_task3, 20, 15, 10, 25)
        
    node.add_event(task_event2)
    node.add_event(task_event3)
        
    assert task_event2 in node.events
    assert task_event3 in node.events
    
def test_remove_event():
    temp_task = TemporalTask("Test", "Example text", start_date=datetime(2025, 10, 1), end_date=datetime(2025, 10, 2))
    task_event = Event(temp_task, 20, 15, 10, 25)
    node = TimeTreeNode(task_event, TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))
        
    temp_task2 = TemporalTask("Make bed", "Remember after waking up to go to bed", start_date=datetime(2025, 10, 1), end_date=datetime(2025, 10, 2))
    temp_task3 = TemporalTask("Reminder", "Remind Jasmine to water her plants", start_date=datetime(2025, 10, 1), end_date=datetime(2025, 10, 2))

    task_event2 = Event(temp_task2, 10, 20, 10, 0)
    task_event3 = Event(temp_task3, 20, 15, 10, 25)
        
    node.add_event(task_event2)
    node.add_event(task_event3)
        
    node.remove_event(0)
        
    assert task_event2 in node.events
    assert task_event3 in node.events

    node.remove_event("Make bed")
        
    assert task_event2 not in node.events
    assert task_event3 in node.events
        
    node.remove_event(task_event3)
        
    assert task_event2 not in node.events
    assert task_event3 not in node.events

def test_remove_event_invalid():
    temp_task = TemporalTask("Test", "Example text", start_date=datetime(2025, 10, 1), end_date=datetime(2025, 10, 2))
    task_event = Event(temp_task, 20, 15, 10, 25)
    node = TimeTreeNode(task_event, TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))
        
    with pytest.raises(IndexError):
        node.remove_event(-1)
    with pytest.raises(ValueError):
        node.remove_event("Anything")
    with pytest.raises(TypeError):
        node.remove_event(datetime(2004, 10, 1))
        
    temp_task2 = TemporalTask("Make bed", "Remember after waking up to go to bed", start_date=datetime(2025, 10, 1), end_date=datetime(2025, 10, 2))
    temp_task3 = TemporalTask("Reminder", "Remind Jasmine to water her plants", start_date=datetime(2025, 10, 1), end_date=datetime(2025, 10, 2))

    task_event2 = Event(temp_task2, 10, 20, 10, 0)
    task_event3 = Event(temp_task3, 20, 15, 10, 25)
        
    node.add_event(task_event2)
    node.add_event(task_event3)
    node.remove_event(task_event)
        
    with pytest.raises(IndexError):
        node.remove_event(-1)
    with pytest.raises(IndexError):
        node.remove_event(1000)
    with pytest.raises(ValueError):
        node.remove_event("Anything")
    with pytest.raises(TypeError):
        node.remove_event(datetime(2004, 10, 1))
    with pytest.raises(ValueError):
        node.remove_event(Event(temp_task, 20, 15, 10, 25))

def test_get_num_events():
    temp_task = TemporalTask("Test", "Example text", start_date=datetime(2025, 10, 1), end_date=datetime(2025, 10, 2))
    task_event = Event(temp_task, 20, 15, 10, 25)
    node = TimeTreeNode(task_event, TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))
        
    assert 1 == node.get_num_events()
        
    temp_task2 = TemporalTask("Make bed", "Remember after waking up to go to bed", start_date=datetime(2025, 10, 1), end_date=datetime(2025, 10, 2))
    temp_task3 = TemporalTask("Reminder", "Remind Jasmine to water her plants", start_date=datetime(2025, 10, 1), end_date=datetime(2025, 10, 2))

    task_event2 = Event(temp_task2, 10, 20, 10, 0)
    task_event3 = Event(temp_task3, 20, 15, 10, 25)
        
    node.add_event(task_event2)
    node.add_event(task_event3)
        
    assert 3 == node.get_num_events()

def test_get_event():
    temp_task = TemporalTask("Test", "Example text", start_date=datetime(2025, 10, 1), end_date=datetime(2025, 10, 2))
    task_event = Event(temp_task, 20, 15, 10, 25)
    node = TimeTreeNode(task_event, TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))
        
    assert task_event == node.get_event(0)
    assert task_event == node.get_event("Test")

def test_get_event_invalid():
    temp_task = TemporalTask("Test", "Example text", start_date=datetime(2025, 10, 1), end_date=datetime(2025, 10, 2))
    task_event = Event(temp_task, 20, 15, 10, 25)
    node = TimeTreeNode(task_event, TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))
        
    with pytest.raises(IndexError):
        node.get_event(-1)
    with pytest.raises(ValueError):
        node.get_event("Anything")
    with pytest.raises(TypeError):
        node.get_event(datetime(2004, 10, 1))
        
    temp_task2 = TemporalTask("Make bed", "Remember after waking up to go to bed", start_date=datetime(2025, 10, 1), end_date=datetime(2025, 10, 2))
    temp_task3 = TemporalTask("Reminder", "Remind Jasmine to water her plants", start_date=datetime(2025, 10, 1), end_date=datetime(2025, 10, 2))

    task_event2 = Event(temp_task2, 10, 20, 10, 0)
    task_event3 = Event(temp_task3, 20, 15, 10, 25)
        
    node.add_event(task_event2)
    node.add_event(task_event3)
    node.remove_event(task_event)
        
    with pytest.raises(IndexError):
        node.get_event(-1)
    with pytest.raises(IndexError):
        node.get_event(1000)
    with pytest.raises(ValueError):
        node.get_event("Anything")
    with pytest.raises(TypeError):
        node.get_event(datetime(2004, 10, 1))

def test_get_events():
    temp_task = TemporalTask("Test", "Example text", start_date=datetime(2025, 10, 1), end_date=datetime(2025, 10, 2))
    task_event = Event(temp_task, 20, 15, 10, 25)
    node = TimeTreeNode(task_event, TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))
        
    assert [task_event] == node.get_events()
        
    temp_task2 = TemporalTask("Make bed", "Remember after waking up to go to bed", start_date=datetime(2025, 10, 1), end_date=datetime(2025, 10, 2))
    temp_task3 = TemporalTask("Reminder", "Remind Jasmine to water her plants", start_date=datetime(2025, 10, 1), end_date=datetime(2025, 10, 2))

    task_event2 = Event(temp_task2, 10, 20, 10, 0)
    task_event3 = Event(temp_task3, 20, 15, 10, 25)
        
    node.add_event(task_event2)
    node.add_event(task_event3)
        
    events = node.get_events()
        
    assert task_event in events
    assert task_event2 in events
    assert task_event3 in events

def test_get_key():
    temp_task = TemporalTask("Test", "Example text", start_date=datetime(2025, 10, 1), end_date=datetime(2025, 10, 2))
    task_event = Event(temp_task, 20, 15, 10, 25)
    node = TimeTreeNode(task_event, TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))
        
    assert TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)) == node.get_key()
    
def test_to_dict():
    temp_task = TemporalTask("Test", "Example text", start_date=datetime(2025, 10, 1), end_date=datetime(2025, 10, 2))
    task_event = Event(temp_task, 20, 15, 10, 25)
    node = TimeTreeNode(task_event, TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))
    
    expected = {'key': {'start_date': '2025-10-01T00:00:00', 'end_date': '2025-10-02T00:00:00'}, 'min': '2025-10-01T00:00:00', 'max': '2025-10-02T00:00:00', 'height': 1, 'events': [{'task': {'type': 'TemporalTask', 'title': 'Test', 'description': 'Example text', 'completed': False, 'deadline': None, 'start_date': '2025-10-01T00:00:00', 'end_date': '2025-10-02T00:00:00', 'startline': None, 'schedule_intervals': [{'start_date': '2025-10-01T00:00:00', 'end_date': '2025-10-02T00:00:00'}]}, 'goal_value': 20, 'routine_value': 15, 'personal_value': 10, 'relational_value': 25}], 'left': None, 'right': None}
    
    assert node.to_dict() == expected
    
def test_from_dict():
    json = {'key': {'start_date': '2025-10-01T00:00:00', 'end_date': '2025-10-02T00:00:00'}, 'min': '2025-10-01T00:00:00', 'max': '2025-10-02T00:00:00', 'height': 1, 'events': [{'task': {'type': 'TemporalTask', 'title': 'Test', 'description': 'Example text', 'completed': False, 'deadline': None, 'start_date': '2025-10-01T00:00:00', 'end_date': '2025-10-02T00:00:00', 'startline': None, 'schedule_intervals': [{'start_date': '2025-10-01T00:00:00', 'end_date': '2025-10-02T00:00:00'}]}, 'goal_value': 20, 'routine_value': 15, 'personal_value': 10, 'relational_value': 25}], 'left': None, 'right': None}
    
    temp_task = TemporalTask("Test", "Example text", start_date=datetime(2025, 10, 1), end_date=datetime(2025, 10, 2))
    task_event = Event(temp_task, 20, 15, 10, 25)
    expected = TimeTreeNode(task_event, TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))
    node = TimeTreeNode.from_dict(json)
    
    assert node == expected