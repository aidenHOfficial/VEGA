import pytest
from datetime import datetime
from models.time_interval import TimeInterval
from models.temporal_task import TemporalTask
from models.time_tree_node import TimeTreeNode
from models.event import Event

def test_add_event():
    temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
    task_event = Event(temp_task, 20, 15, 10, 25)
    node = TimeTreeNode(task_event, TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))
        
    temp_task2 = TemporalTask("Make bed", "Remember after waking up to go to bed", datetime(2025, 10, 1), datetime(2025, 10, 2))
    temp_task3 = TemporalTask("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1), datetime(2025, 10, 2))

    task_event2 = Event(temp_task2, 10, 20, 10, 0)
    task_event3 = Event(temp_task3, 20, 15, 10, 25)
        
    node.add_event(task_event2)
    node.add_event(task_event3)
        
    assert task_event2 in node.events
    assert task_event3 in node.events
    
def test_remove_event():
    temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
    task_event = Event(temp_task, 20, 15, 10, 25)
    node = TimeTreeNode(task_event, TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))
        
    temp_task2 = TemporalTask("Make bed", "Remember after waking up to go to bed", datetime(2025, 10, 1), datetime(2025, 10, 2))
    temp_task3 = TemporalTask("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1), datetime(2025, 10, 2))

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
    temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
    task_event = Event(temp_task, 20, 15, 10, 25)
    node = TimeTreeNode(task_event, TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))
        
    with pytest.raises(IndexError):
        node.remove_event(-1)
    with pytest.raises(ValueError):
        node.remove_event("Anything")
    with pytest.raises(TypeError):
        node.remove_event(datetime(2004, 10, 1))
        
    temp_task2 = TemporalTask("Make bed", "Remember after waking up to go to bed", datetime(2025, 10, 1), datetime(2025, 10, 2))
    temp_task3 = TemporalTask("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1), datetime(2025, 10, 2))

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
    temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
    task_event = Event(temp_task, 20, 15, 10, 25)
    node = TimeTreeNode(task_event, TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))
        
    assert 1 == node.get_num_events()
        
    temp_task2 = TemporalTask("Make bed", "Remember after waking up to go to bed", datetime(2025, 10, 1), datetime(2025, 10, 2))
    temp_task3 = TemporalTask("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1), datetime(2025, 10, 2))

    task_event2 = Event(temp_task2, 10, 20, 10, 0)
    task_event3 = Event(temp_task3, 20, 15, 10, 25)
        
    node.add_event(task_event2)
    node.add_event(task_event3)
        
    assert 3 == node.get_num_events()

def test_get_event():
    temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
    task_event = Event(temp_task, 20, 15, 10, 25)
    node = TimeTreeNode(task_event, TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))
        
    assert task_event == node.get_event(0)
    assert task_event == node.get_event("Test")

def test_get_event_invalid():
    temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
    task_event = Event(temp_task, 20, 15, 10, 25)
    node = TimeTreeNode(task_event, TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))
        
    with pytest.raises(IndexError):
        node.get_event(-1)
    with pytest.raises(ValueError):
        node.get_event("Anything")
    with pytest.raises(TypeError):
        node.get_event(datetime(2004, 10, 1))
        
    temp_task2 = TemporalTask("Make bed", "Remember after waking up to go to bed", datetime(2025, 10, 1), datetime(2025, 10, 2))
    temp_task3 = TemporalTask("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1), datetime(2025, 10, 2))

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
    temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
    task_event = Event(temp_task, 20, 15, 10, 25)
    node = TimeTreeNode(task_event, TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))
        
    assert [task_event] == node.get_events()
        
    temp_task2 = TemporalTask("Make bed", "Remember after waking up to go to bed", datetime(2025, 10, 1), datetime(2025, 10, 2))
    temp_task3 = TemporalTask("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1), datetime(2025, 10, 2))

    task_event2 = Event(temp_task2, 10, 20, 10, 0)
    task_event3 = Event(temp_task3, 20, 15, 10, 25)
        
    node.add_event(task_event2)
    node.add_event(task_event3)
        
    events = node.get_events()
        
    assert task_event in events
    assert task_event2 in events
    assert task_event3 in events

def test_get_key():
    temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
    task_event = Event(temp_task, 20, 15, 10, 25)
    node = TimeTreeNode(task_event, TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))
        
    assert TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)) == node.get_key()