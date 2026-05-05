import pytest
from datetime import datetime
from models.time_interval import TimeInterval
from models.temporal_task import TemporalTask
from models.time_tree import TimeTree
from models.event import Event

def test_insertion():
    tree = TimeTree()
        
    temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
    task_event = Event(temp_task, 20, 15, 10, 25)
    tree.insert(task_event)

    assert task_event, tree.search(TimeInterval(datetime(2025, 10, 1) == datetime(2025, 10, 2))).get_event("Test")

    temp_task2 = TemporalTask("Make bed", "Remember after waking up to go to bed", datetime(2025, 10, 3), datetime(2025, 10, 4))
    task_event2 = Event(temp_task2, 10, 20, 10, 25)
    tree.insert(task_event2)

    temp_task3 = TemporalTask("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1), datetime(2025, 10, 2))
    task_event3 = Event(temp_task3, 20, 15, 10, 25)
    tree.insert(task_event3)

    assert task_event3 == tree.search(TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2))).get_event("Reminder")
    assert 2 ==  tree.search(TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2))).get_num_events()

    temp_task4 = TemporalTask("Another", "Example text", datetime(2025, 10, 5), datetime(2025, 10, 6))
    task_event4 = Event(temp_task4, 20, 15, 10, 25)
    tree.insert(task_event4)

    assert task_event4 == tree.search(TimeInterval(datetime(2025, 10, 5), datetime(2025, 10, 6))).get_event("Another")

def test_insertion_multiple_schedule_intervals():
    tree = TimeTree()
        
    temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2), None, None, [TimeInterval(datetime(2025, 11, 1), datetime(2025, 11, 2)), TimeInterval(datetime(2025, 10, 5), datetime(2025, 10, 6))])
    task_event = Event(temp_task, 20, 15, 10, 25)
    tree.insert(task_event)

    assert task_event == tree.search(TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2))).get_event("Test")
    assert task_event == tree.search(TimeInterval(datetime(2025, 11, 1), datetime(2025, 11, 2))).get_event("Test")
    assert task_event == tree.search(TimeInterval(datetime(2025, 10, 5), datetime(2025, 10, 6))).get_event("Test")
    assert 3 == tree.get_size()

def test_get_size():
    tree = TimeTree()
        
    assert 0 == tree.get_size()
        
    temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
    task_event = Event(temp_task, 20, 15, 10, 25)
    tree.insert(task_event)

    assert 1 == tree.get_size()

    temp_task2 = TemporalTask("Make bed", "Remember after waking up to go to bed", datetime(2025, 10, 3), datetime(2025, 10, 4))
    task_event2 = Event(temp_task2, 10, 20, 10, 25)
    tree.insert(task_event2)

    assert 2 == tree.get_size()

    temp_task3 = TemporalTask("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1), datetime(2025, 10, 2))
    task_event3 = Event(temp_task3, 20, 15, 10, 25)
    tree.insert(task_event3)

    assert 2 == tree.get_size()

    tree.delete(task_event)

    assert 2 == tree.get_size()

    tree.delete(task_event3)

    assert 1 == tree.get_size()

def test_delete():
    tree = TimeTree()
        
    temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
    task_event = Event(temp_task, 20, 15, 10, 25)
    tree.insert(task_event)

    temp_task2 = TemporalTask("Make bed", "Remember after waking up to go to bed", datetime(2025, 10, 3), datetime(2025, 10, 4))
    task_event2 = Event(temp_task2, 10, 20, 10, 25)
    tree.insert(task_event2)

    temp_task3 = TemporalTask("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1), datetime(2025, 10, 2))
    task_event3 = Event(temp_task3, 20, 15, 10, 25)
    tree.insert(task_event3)

    assert 2 == tree.search(TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2))).get_num_events()

    tree.delete(task_event)

    assert 1 == tree.search(TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2))).get_num_events()
    assert task_event3 == tree.search(TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2))).get_event("Reminder")

    tree.delete(task_event3)

    with pytest.raises(ValueError):
        tree.search(TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))

def test_overlap_search():
    tree = TimeTree()
        
    temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
    task_event = Event(temp_task, 20, 15, 10, 25)
    tree.insert(task_event)

    temp_task2 = TemporalTask("Test", "Example text", datetime(2025, 10, 4), datetime(2025, 10, 6))
    task_event2 = Event(temp_task2, 20, 15, 10, 25)
    tree.insert(task_event2)

    temp_task3 = TemporalTask("Test", "Example text", datetime(2025, 10, 2), datetime(2025, 10, 4))
    task_event3 = Event(temp_task3, 20, 15, 10, 25)
    tree.insert(task_event3)

    events = [task_event, task_event2, task_event3]

    search_events = tree.overlap_search(TimeInterval(datetime(2025, 10, 2), datetime(2025, 10, 4)))
    assert 3 == len(search_events)
    for event in search_events:
        assert event['event'] in events

def test_search():
    tree = TimeTree()
        
    temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
    task_event = Event(temp_task, 20, 15, 10, 25)
    tree.insert(task_event)

    assert task_event == tree.search(TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2))).get_event("Test")

def test_search_invalid():
    tree = TimeTree()
        
    temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
    task_event = Event(temp_task, 20, 15, 10, 25)
    tree.insert(task_event)

    with pytest.raises(ValueError):
        tree.search(TimeInterval(datetime(2025, 10, 2), datetime(2025, 10, 3)))
        
def test_to_dict():
    tree = TimeTree()
        
    temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
    task_event = Event(temp_task, 20, 15, 10, 25)
    tree.insert(task_event)

    temp_task2 = TemporalTask("Test", "Example text", datetime(2025, 10, 4), datetime(2025, 10, 6))
    task_event2 = Event(temp_task2, 20, 15, 10, 25)
    tree.insert(task_event2)

    temp_task3 = TemporalTask("Test", "Example text", datetime(2025, 10, 2), datetime(2025, 10, 4))
    task_event3 = Event(temp_task3, 20, 15, 10, 25)
    tree.insert(task_event3)
    
    expected =  {'_size': 3, '_root': {'key': {'start_date': '2025-10-02T00:00:00', 'end_date': '2025-10-04T00:00:00'}, 'min': '2025-10-02T00:00:00', 'max': '2025-10-06T00:00:00', 'height': 2, 'events': [{'_task': {'_type': 'TemporalTask', '_title': 'Test', '_description': 'Example text', '_completed': False, '_deadline': None, '_start_date': '2025-10-02T00:00:00', '_end_date': '2025-10-04T00:00:00', '_startline': None, '_schedule_intervals': [{'start_date': '2025-10-02T00:00:00', 'end_date': '2025-10-04T00:00:00'}]}, '_goal_value': 20, '_routine_value': 15, '_personal_value': 10, '_relational_value': 25}], 'left': {'key': {'start_date': '2025-10-01T00:00:00', 'end_date': '2025-10-02T00:00:00'}, 'min': '2025-10-01T00:00:00', 'max': '2025-10-02T00:00:00', 'height': 1, 'events': [{'_task': {'_type': 'TemporalTask', '_title': 'Test', '_description': 'Example text', '_completed': False, '_deadline': None, '_start_date': '2025-10-01T00:00:00', '_end_date': '2025-10-02T00:00:00', '_startline': None, '_schedule_intervals': [{'start_date': '2025-10-01T00:00:00', 'end_date': '2025-10-02T00:00:00'}]}, '_goal_value': 20, '_routine_value': 15, '_personal_value': 10, '_relational_value': 25}], 'left': None, 'right': None}, 'right': {'key': {'start_date': '2025-10-04T00:00:00', 'end_date': '2025-10-06T00:00:00'}, 'min': '2025-10-04T00:00:00', 'max': '2025-10-06T00:00:00', 'height': 1, 'events': [{'_task': {'_type': 'TemporalTask', '_title': 'Test', '_description': 'Example text', '_completed': False, '_deadline': None, '_start_date': '2025-10-04T00:00:00', '_end_date': '2025-10-06T00:00:00', '_startline': None, '_schedule_intervals': [{'start_date': '2025-10-04T00:00:00', 'end_date': '2025-10-06T00:00:00'}]}, '_goal_value': 20, '_routine_value': 15, '_personal_value': 10, '_relational_value': 25}], 'left': None, 'right': None}}}   
    assert expected == tree.to_dict()
    
def test_from_dict():
    json =  {'_size': 3, '_nodes': {'key': {'start_date': '2025-10-02T00:00:00', 'end_date': '2025-10-04T00:00:00'}, 'min': '2025-10-02T00:00:00', 'max': '2025-10-06T00:00:00', 'height': 2, 'events': [{'_task': {'_type': 'TemporalTask', '_title': 'Test', '_description': 'Example text', '_completed': False, '_deadline': None, '_start_date': '2025-10-02T00:00:00', '_end_date': '2025-10-04T00:00:00', '_startline': None, '_schedule_intervals': [{'start_date': '2025-10-02T00:00:00', 'end_date': '2025-10-04T00:00:00'}]}, '_goal_value': 20, '_routine_value': 15, '_personal_value': 10, '_relational_value': 25}], 'left': {'key': {'start_date': '2025-10-01T00:00:00', 'end_date': '2025-10-02T00:00:00'}, 'min': '2025-10-01T00:00:00', 'max': '2025-10-02T00:00:00', 'height': 1, 'events': [{'_task': {'_type': 'TemporalTask', '_title': 'Test', '_description': 'Example text', '_completed': False, '_deadline': None, '_start_date': '2025-10-01T00:00:00', '_end_date': '2025-10-02T00:00:00', '_startline': None, '_schedule_intervals': [{'start_date': '2025-10-01T00:00:00', 'end_date': '2025-10-02T00:00:00'}]}, '_goal_value': 20, '_routine_value': 15, '_personal_value': 10, '_relational_value': 25}], 'left': None, 'right': None}, 'right': {'key': {'start_date': '2025-10-04T00:00:00', 'end_date': '2025-10-06T00:00:00'}, 'min': '2025-10-04T00:00:00', 'max': '2025-10-06T00:00:00', 'height': 1, 'events': [{'_task': {'_type': 'TemporalTask', '_title': 'Test', '_description': 'Example text', '_completed': False, '_deadline': None, '_start_date': '2025-10-04T00:00:00', '_end_date': '2025-10-06T00:00:00', '_startline': None, '_schedule_intervals': [{'start_date': '2025-10-04T00:00:00', 'end_date': '2025-10-06T00:00:00'}]}, '_goal_value': 20, '_routine_value': 15, '_personal_value': 10, '_relational_value': 25}], 'left': None, 'right': None}}}   
    tree = TimeTree.from_dict(json)
    
    expected = TimeTree()
        
    temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
    task_event = Event(temp_task, 20, 15, 10, 25)
    expected.insert(task_event)

    temp_task2 = TemporalTask("Test", "Example text", datetime(2025, 10, 4), datetime(2025, 10, 6))
    task_event2 = Event(temp_task2, 20, 15, 10, 25)
    expected.insert(task_event2)

    temp_task3 = TemporalTask("Test", "Example text", datetime(2025, 10, 2), datetime(2025, 10, 4))
    task_event3 = Event(temp_task3, 20, 15, 10, 25)
    expected.insert(task_event3)
    
    assert tree == expected

# def test_sweepline_overlap_search(self):
#     # TODO: Test this overlap search function
#     pass