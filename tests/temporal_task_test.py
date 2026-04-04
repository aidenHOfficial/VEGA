import pytest
from datetime import datetime, timedelta
from models.temporal_task import TemporalTask
from models.time_interval import TimeInterval

def test_constructor_with_invalid_dates():
    with pytest.raises(ValueError):
        TemporalTask("test", "this is a test task", datetime(2025, 10, 1), datetime(2020, 10, 1))

def test_constructor_with_out_of_scope_lines():
    with pytest.raises(ValueError):
        TemporalTask("test", "this is a test task", datetime(2025, 9, 1), datetime(2025, 10, 2), datetime(2025, 9, 2), datetime(2025, 10, 2))
        
    with pytest.raises(ValueError):
        TemporalTask("test", "this is a test task", datetime(2025, 9, 1), datetime(2025, 10, 2), startline=datetime(2025, 9, 2))

    with pytest.raises(ValueError):
        TemporalTask("test", "this is a test task", datetime(2025, 9, 2), datetime(2025, 10, 2), deadline=datetime(2025, 10, 1))
    
    reschedules = [TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)), TimeInterval(datetime(2025, 10, 3), datetime(2025, 10, 4))]
    with pytest.raises(ValueError):
        TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10), deadline=datetime(2025, 10, 9), schedule_intervals=reschedules)
        
    with pytest.raises(ValueError):
        TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10), startline=datetime(2025, 10, 2), schedule_intervals=reschedules)

def test_get_start_date():
    task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10))
    assert task.get_start_date() == datetime(2025, 10, 2)

def test_get_end_date():
    task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10))
    assert task.get_end_date() == datetime(2025, 10, 10)
    
def test_get_startline():
    task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10), datetime(2025, 10, 2))
    assert task.get_startline() == datetime(2025, 10, 2)

def test_get_total_time():
    task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10))
    assert task.get_total_time() == datetime(2025, 10, 10) - datetime(2025, 10, 2)

def test_get_time_slot():
    task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10))
    assert task.get_time_slot() == TimeInterval(datetime(2025, 10, 2), datetime(2025, 10, 10))

def test_get_schedule_interval_no_values():
    task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10))
    assert task.get_schedule_intervals() == [TimeInterval(datetime(2025, 10, 2), datetime(2025, 10, 10))]

def test_get_schedule_interval_with_values():
    task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10), schedule_intervals=[TimeInterval(datetime(2025, 10, 3), datetime(2025, 10, 11))])
    assert task.get_schedule_intervals() == [TimeInterval(datetime(2025, 10, 2), datetime(2025, 10, 11))]

def test_get_duration():
    task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10), schedule_intervals=[TimeInterval(datetime(2025, 10, 3), datetime(2025, 10, 11))])
    assert task.get_duration() == timedelta(8)

def test_add_schedule_interval():
    task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10))
    task.add_schedule_interval(TimeInterval(datetime(2025, 10, 3), datetime(2025, 10, 11)))
    assert task.get_schedule_intervals() == [TimeInterval(datetime(2025, 10, 2), datetime(2025, 10, 11))]
        
    task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10), datetime(2025, 10, 2), datetime(2025, 10, 10))
    task.add_schedule_interval(TimeInterval(datetime(2025, 10, 2), datetime(2025, 10, 10)))
    assert task.get_schedule_intervals() == [TimeInterval(datetime(2025, 10, 2), datetime(2025, 10, 10))]
        
def test_add_schedule_interval_invalid_values():
    task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10), datetime(2025, 10, 2), datetime(2025, 10, 10))
    with pytest.raises(ValueError):
        pytest.raises(ValueError, task.add_schedule_interval(TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 10))))
    with pytest.raises(ValueError):
        pytest.raises(ValueError, task.add_schedule_interval(TimeInterval(datetime(2025, 10, 2), datetime(2025, 10, 12))))

def test_to_dict():
    task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10), datetime(2025, 10, 2), datetime(2025, 10, 10))
    expected = {
        '_completed': False,
        '_deadline': '2025-10-10T00:00:00',
        '_description': 'this is a test task',
        '_end_date': '2025-10-10T00:00:00',
        '_schedule_intervals': [
            {
                'end_date': '2025-10-10T00:00:00',
                'start_date': '2025-10-02T00:00:00',
            },
        ],
        '_start_date': '2025-10-02T00:00:00',
        '_startline': '2025-10-02T00:00:00',
        '_title': 'test',
    }
    
    assert task.to_dict() == expected