import pytest
from datetime import datetime, timedelta
from app.models.time_interval import TimeInterval

def test___init__():
    assert TimeInterval(datetime(2004, 10, 1), datetime(2004, 10, 2)) is not None

def test___init___invalid():
    with pytest.raises(ValueError):
        _ = TimeInterval(datetime(2004, 11, 1), datetime(2004, 10, 2))
    
def test_get_start_date():
    interval = TimeInterval(datetime(2004, 10, 1), datetime(2004, 10, 2))
    assert datetime(2004, 10, 1) == interval.get_start_date()
    assert datetime(2004, 10, 1) == interval.start_date

def test_get_end_date():
    interval = TimeInterval(datetime(2004, 10, 1), datetime(2004, 10, 2))
    assert datetime(2004, 10, 2) == interval.get_end_date()
    assert datetime(2004, 10, 2) == interval.end_date

def test_get_interval():
    interval = TimeInterval(datetime(2004, 10, 1), datetime(2004, 10, 2))
    assert (datetime(2004, 10, 1), datetime(2004, 10, 2)) == interval.get_interval()
     
def test_get_duration():
    dur = timedelta(1)
    interval = TimeInterval(datetime(2004, 10, 1), datetime(2004, 10, 2))
    assert interval.get_duration() == dur

def test_to_dict():
    interval = TimeInterval(datetime(2004, 10, 1), datetime(2004, 10, 2))
    expected = {
        "start_date": datetime(2004, 10, 1).isoformat(),
        "end_date": datetime(2004, 10, 2).isoformat()
    }
    assert interval.to_dict() == expected
    
def test_from_dict():
    json = {
        "start_date": datetime(2004, 10, 1).isoformat(),
        "end_date": datetime(2004, 10, 2).isoformat()
    }
    interval = TimeInterval.from_dict(json)
    expected = TimeInterval(datetime(2004, 10, 1), datetime(2004, 10, 2))
    
    assert interval == expected