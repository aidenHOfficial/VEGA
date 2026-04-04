import pytest
from datetime import datetime, timedelta
from models.temporal_task import TemporalTask
from models.task import Task
from models.routine import Routine

def test_add_task():
    routine = Routine("Routine", "Example text", datetime(2025, 1, 1), datetime(2025, 1, 2))

    temp_task = TemporalTask("Task A", "Example text", datetime(2025, 1, 1, 8), datetime(2025, 1, 1, 10))
    routine.add_task(temp_task)
    assert temp_task in routine._tasks

    non_temp_task = Task("Task B", "Example Text")
    routine.add_task(non_temp_task, timedelta(hours=1))
    assert non_temp_task in routine._tasks

def test_add_task_invalid():
    routine = Routine("Routine", "Example text", datetime(2025, 1, 1), datetime(2025, 1, 2))
    non_temp_task = Task("Task A", "No complete time provided")

    with pytest.raises(ValueError):
        routine.add_task(non_temp_task)
    with pytest.raises(ValueError):
        routine.add_task(non_temp_task, 0)

def test_get_tasks():
    check_list = []
    routine = Routine("Routine", "Example text", datetime(2025, 1, 1, 2), datetime(2025, 1, 2))

    assert check_list == routine.get_tasks()

    task_A = Task("Task A", "Example text")
    task_B = TemporalTask("Task B", "Example text", datetime(2025, 1, 1, 2), datetime(2025, 1, 1, 3))

    routine.add_task(task_A, timedelta(10))
    routine.add_task(task_B)

    check_list.extend([task_A, task_B])

    for item in routine.get_tasks():
        assert item in check_list

def test_get_task():
    routine = Routine("Routine", "Example text", datetime(2025, 1, 1), datetime(2025, 1, 2))

    task_A = Task("Task A", "Example text")
    task_B = TemporalTask("Task B", "Example text", datetime(2025, 1, 1, 2), datetime(2025, 1, 1, 3))

    routine.add_task(task_A, timedelta(10))
    routine.add_task(task_B)

    assert task_A, routine.get_task(0)
    assert task_B, routine.get_task(1)
    assert task_A, routine.get_task("Task A")
    assert task_B, routine.get_task("Task B")

def test_get_task_invalid():
    routine = Routine("Routine", "Example text", datetime(2025, 1, 1), datetime(2025, 1, 2))

    with pytest.raises(IndexError):
        routine.get_task(0)
    with pytest.raises(ValueError):
        routine.get_task("Anything")

    task_A = Task("Task A", "Example text")
    task_B = TemporalTask("Task B", "Example text", datetime(2025, 1, 1, 2), datetime(2025, 1, 1, 3))

    routine.add_task(task_A, timedelta(10))
    routine.add_task(task_B)

    with pytest.raises(IndexError):
        routine.get_task(-1)
    with pytest.raises(IndexError):
        routine.get_task(1000)
    with pytest.raises(TypeError):
        routine.get_task(datetime(2004, 10, 1))
    with pytest.raises(ValueError):
        routine.get_task("Anything")

def test_get_task_complete_time():
    routine = Routine("Routine", "Example text", datetime(2025, 1, 1), datetime(2025, 1, 2))

    task_A = Task("Task A", "Example text")
    task_B = TemporalTask("Task B", "Example text", datetime(2025, 1, 1, 2), datetime(2025, 1, 1, 3))

    routine.add_task(task_A, timedelta(10))
    routine.add_task(task_B)

    assert timedelta(10) == routine.get_task_complete_time(0)
    assert task_B.get_total_time() == routine.get_task_complete_time(1)
    assert timedelta(10) == routine.get_task_complete_time("Task A")
    assert task_B.get_total_time() == routine.get_task_complete_time("Task B")

def test_get_task_complete_time_invalid():
    routine = Routine("Routine", "Example text", datetime(2025, 1, 1), datetime(2025, 1, 2))

    with pytest.raises(IndexError):
        routine.get_task_complete_time(0)
    with pytest.raises(ValueError):
        routine.get_task_complete_time("Anything")

    task_A = Task("Task A", "Example text")
    task_B = TemporalTask("Task B", "Example text", datetime(2025, 1, 1, 2), datetime(2025, 1, 1, 3))

    routine.add_task(task_A, timedelta(10))
    routine.add_task(task_B)

    with pytest.raises(IndexError):
        routine.get_task_complete_time(-1)
    with pytest.raises(IndexError):
        routine.get_task_complete_time(1000)
    with pytest.raises(TypeError):
        routine.get_task_complete_time(datetime(2004, 10, 1))
    with pytest.raises(ValueError):
        routine.get_task_complete_time("Anything")

def test_get_estimated_time():
    routine = Routine("Routine", "Example text", datetime(2025, 1, 1, 2, 0), datetime(2025, 1, 1, 3, 0))

    assert routine.get_estimated_time() == timedelta(0, 0)
    assert routine.total_estimated_time == timedelta(0, 0)

    task_A = Task("Task A", "Example text")
    task_B = TemporalTask("Task B", "Example text", datetime(2025, 10, 1, 2), datetime(2025, 10, 1, 3))

    routine.add_task(task_A, timedelta(0, 0, 0, 0, 30, 0, 0))
    routine.add_task(task_B)

    assert routine.get_estimated_time() == (timedelta(0, 0, 0, 0, 30, 0, 0) + (datetime(2025, 10, 1, 3) - datetime(2025, 10, 1, 2)))
    assert routine.total_estimated_time == (timedelta(0, 0, 0, 0, 30, 0, 0) + (datetime(2025, 10, 1, 3) - datetime(2025, 10, 1, 2)))

def test_remove_task():
    routine = Routine("Routine", "Example text", datetime(2025, 1, 1, 2, 0), datetime(2025, 1, 1, 3, 0))

    task_A = Task("Task A", "Example text")
    task_B = TemporalTask("Task B", "Example text", datetime(2025, 10, 1, 2), datetime(2025, 10, 1, 3))

    routine.add_task(task_A, timedelta(0, 0, 0, 0, 30, 0, 0))
    routine.add_task(task_B)

    routine.remove_task(0)

    tasks = routine.get_tasks()
    for task in tasks:
        assert task != task_A

    routine.remove_task("Task B")

    tasks = routine.get_tasks()
    for task in tasks:
        assert task != task_A
        assert task != task_B

def test_remove_task_invalid():
    routine = Routine("Routine", "Example text", datetime(2025, 1, 1, 2, 0), datetime(2025, 1, 1, 3, 0))

    with pytest.raises(IndexError):
        routine.remove_task(0)
    with pytest.raises(ValueError):
        routine.remove_task("asdf")

    task_A = Task("Task A", "Example text")
    task_B = TemporalTask("Task B", "Example text", datetime(2025, 10, 1, 2), datetime(2025, 10, 1, 3))

    routine.add_task(task_A, timedelta(0, 0, 0, 0, 30, 0, 0))
    routine.add_task(task_B)

    with pytest.raises(ValueError):
        routine.remove_task("Task C")
    with pytest.raises(IndexError):
        routine.remove_task(1000)
    with pytest.raises(IndexError):
        routine.remove_task(-1)
    with pytest.raises(TypeError):
        routine.remove_task(datetime(0))

def test_change_order():
    routine = Routine("Routine", "Example text", datetime(2025, 1, 1, 2, 0), datetime(2025, 1, 1, 3, 0))
    task_A = Task("Task A", "Example text")
    task_B = TemporalTask("Task B", "Example text", datetime(2025, 10, 1, 2), datetime(2025, 10, 1, 3))
    routine.add_task(task_A, timedelta(0, 0, 0, 0, 30, 0, 0))
    routine.add_task(task_B)

    reorder = [task_B, task_A]
    routine.change_order(reorder)

    assert reorder == routine.get_tasks()
        
def test_change_order_invalid():
    routine = Routine("Routine", "Example text", datetime(2025, 1, 1, 2, 0), datetime(2025, 1, 1, 3, 0))
    task_A = Task("Task A", "Example text")
    task_B = TemporalTask("Task B", "Example text", datetime(2025, 10, 1, 2), datetime(2025, 10, 1, 3))
    routine.add_task(task_A, timedelta(0, 0, 0, 0, 30, 0, 0))
    routine.add_task(task_B)

    reorder = [task_B]

    with pytest.raises(ValueError):
        routine.change_order(reorder)

    task_C = Task("Task C", "Example text")
    reorder = [task_B, task_A, task_C]

    with pytest.raises(ValueError):
        routine.change_order(reorder)

def test_change_task_complete_time():
    routine = Routine("Routine", "Example text", datetime(2025, 1, 1, 2, 0), datetime(2025, 1, 1, 3, 0))

    task_A = Task("Task A", "Example text")
    task_B = TemporalTask("Task B", "Example text", datetime(2025, 10, 1, 2), datetime(2025, 10, 1, 3))

    routine.add_task(task_A, timedelta(0, 0, 0, 0, 30, 0, 0))
    routine.add_task(task_B)
    routine.change_task_complete_time(0, timedelta(0, 0, 0, 0, 15, 0, 0))

    assert timedelta(0, 0, 0, 0, 15, 0, 0) == routine.get_task_complete_time(0)

    routine.change_task_complete_time("Task A", timedelta(0, 0, 0, 0, 30, 0, 0))

    assert timedelta(0, 0, 0, 0, 30, 0, 0) == routine.get_task_complete_time("Task A")
        
def test_change_task_complete_time_invalid():
    routine = Routine("Routine", "Example text", datetime(2025, 1, 1, 2, 0), datetime(2025, 1, 1, 3, 0))

    with pytest.raises(IndexError):
        routine.change_task_complete_time(0, timedelta(0, 0, 0, 0, 15, 0, 0))
    with pytest.raises(ValueError):
        routine.change_task_complete_time("asdf", timedelta(0, 0, 0, 0, 15, 0, 0))

    task_A = Task("Task A", "Example text")
    task_B = TemporalTask("Task B", "Example text", datetime(2025, 10, 1, 2), datetime(2025, 10, 1, 3))

    routine.add_task(task_A, timedelta(0, 0, 0, 0, 30, 0, 0))
    routine.add_task(task_B)

    routine.change_task_complete_time("Task A", timedelta(0, 0, 0, 0, 15, 0, 0))

    with pytest.raises(ValueError):
        routine.change_task_complete_time("Task C", timedelta(0, 0, 0, 0, 30, 0, 0))
    with pytest.raises(IndexError):
        routine.change_task_complete_time(1000, timedelta(0, 0, 0, 0, 30, 0, 0))
    with pytest.raises(IndexError):
        routine.change_task_complete_time(-1, timedelta(0, 0, 0, 0, 30, 0, 0))
    with pytest.raises(TypeError):
        routine.change_task_complete_time(datetime(0), timedelta(0, 0, 0, 0, 30, 0, 0))

def test_get_next_time_slot():
    routine = Routine("Routine", "Example text", datetime(2025, 1, 1, 2, 0), datetime(2025, 1, 1, 3, 0))

    assert datetime(2025, 1, 1, 2, 0) + timedelta(1), datetime(2025, 1, 1, 3, 0) + timedelta(1) == routine.get_next_time_slot(1)
    assert datetime(2025, 1, 1, 2, 0) + timedelta(2), datetime(2025, 1, 1, 3, 0) + timedelta(2) == routine.get_next_time_slot(2)

    routine = Routine("Routine", "Example text", datetime(2025, 1, 1, 2, 0), datetime(2025, 1, 1, 3, 0), timedelta(0, 0, 0, 0, 0, 0, 1))

    assert datetime(2025, 1, 1, 2, 0) + timedelta(0, 0, 0, 0, 0, 0, 1), datetime(2025, 1, 1, 3, 0) + timedelta(0, 0, 0, 0, 0, 0, 1) == routine.get_next_time_slot(1)
    assert datetime(2025, 1, 1, 2, 0) + timedelta(0, 0, 0, 0, 0, 0, 2), datetime(2025, 1, 1, 3, 0) + timedelta(0, 0, 0, 0, 0, 0, 2) == routine.get_next_time_slot(2)

def test_get_next_time_slot_invalid():
    routine = Routine("Routine", "Example text", datetime(2025, 1, 1, 2, 0), datetime(2025, 1, 1, 3, 0))

    with pytest.raises(ValueError):
        routine.get_next_time_slot(0)
    with pytest.raises(ValueError):
        routine.get_next_time_slot(-1)

    routine = Routine("Routine", "Example text", datetime(2025, 1, 1, 2, 0), datetime(2025, 1, 1, 3, 0), timedelta(0, 0, 0, 0, 0, 0, 1))

    with pytest.raises(ValueError):
        routine.get_next_time_slot(0)
    with pytest.raises(ValueError):
        routine.get_next_time_slot(-1)

def test_to_dict():
    routine = Routine("Routine", "Example text", datetime(2025, 1, 1, 2, 0), datetime(2025, 1, 1, 3, 0))
    task_A = Task("Task A", "Example text")
    task_B = TemporalTask("Task B", "Example text", datetime(2025, 10, 1, 2), datetime(2025, 10, 1, 3))
    routine.add_task(task_A, timedelta(0, 0, 0, 0, 30, 0, 0))
    routine.add_task(task_B)

    print(f"routine.to_dict(): {routine.to_dict()}")

    expected = {

    }

    assert expected == routine.to_dict()