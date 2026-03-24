import pytest
from datetime import datetime
from models.task import Task

def test_failed_constructor():
    task = Task("this is a test task", datetime(2004,1,1))
    assert task is not None

def test_constructor_with_deadline():
    task = Task("test", "this is a test task", datetime(2004,1,1))
    assert task is not None

def test_constructor_without_deadline():
    task = Task("test", "this is a test task")
    assert task is not None
    
def test_get_completion_status():
    task = Task("test", "this is a test task")
    assert False == task.get_completion_status()

    task._completed = True
    assert True == task.get_completion_status()

def test_get_title():
    task = Task("test", "this is a test task")
    assert task.get_title() == "test"

    task_complicated_title = Task("27hsiae7ifkiashie", "this is a test task")
    assert task_complicated_title.get_title() == "27hsiae7ifkiashie"

def test_get_description():
    task = Task("test", "this is a test task")
    assert task.get_description() == "this is a test task"

    task_complicated_description = Task("test", "new description")
    assert task_complicated_description.get_description() == "new description"

def test_get_deadline_with_set_deadline():
    task = Task("test", "this is a test task", datetime(2004, 10, 1))
    assert task.get_deadline() == datetime(2004, 10, 1)

def test_get_deadline_with_no_deadline():
    task = Task("test", "this is a test task")
    assert task.get_deadline() == None