import pytest
from datetime import datetime
from models.temporal_task import TemporalTask
from models.task import Task
from models.goal import Goal

@pytest.fixture
def dummy_goal():
    goal = Goal("Root Goal", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3), datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3))
        
    task = Task("Task", "Example text", datetime(2026, 5, 1))
    temp_task = TemporalTask("Dummy Temporal Task", "Example text", datetime(2025, 10, 10), datetime(2025, 10, 17))
        
    sub_goal_A = Goal("Subgoal A", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 3, 30), datetime(2025, 10, 1, 2), datetime(2026, 3, 30))
    sub_goal_AA = Goal("Subgoal AA", "Example text", datetime(2025, 10, 1, 2), datetime(2025, 12, 30), datetime(2025, 10, 1, 2), datetime(2025, 12, 30))
        
    sub_goal_B = Goal("Subgoal B", "Example text", datetime(2026, 3, 30), datetime(2026, 10, 1, 2), datetime(2026, 3, 30), datetime(2026, 10, 1, 2))
    sub_goal_BA = Goal("Subgoal BA", "Example text", datetime(2026, 3, 30), datetime(2026, 5, 1), datetime(2026, 3, 30), datetime(2026, 5, 1))
    sub_goal_BB = Goal("Subgoal BB", "Example text", datetime(2026, 5, 1), datetime(2026, 10, 1), datetime(2026, 5, 1), datetime(2026, 10, 1))
        
    sub_goal_A.add_subgoal(sub_goal_AA)
        
    sub_goal_B.add_subgoal(sub_goal_BA)
    sub_goal_B.add_subgoal(sub_goal_BB)
    sub_goal_B.add_subgoal(task)
        
    goal.add_subgoal(temp_task)
    goal.add_subgoal(sub_goal_A)
    goal.add_subgoal(sub_goal_B)
        
    return goal

def test_add_subgoal(dummy_goal: Goal):
    sub_goal_A = dummy_goal.get_subgoal_by_title("Subgoal A")
    sub_goal_AB = Goal("Subgoal AB", "this is a dummy goal", datetime(2025, 10, 1, 2), datetime(2026, 3, 30))
    sub_goal_A.add_subgoal(sub_goal_AB)
        
    assert sub_goal_AB, dummy_goal.get_subgoal("Subgoal A").get_subgoal("Subgoal AB")
       
def test_add_subgoal_invalid(dummy_goal: Goal):
    sub_goal_A = dummy_goal.get_subgoal_by_title("Subgoal A")
    sub_goal_AB = Goal("Subgoal AB", "this is a dummy goal", datetime(2024, 10, 1), datetime(2026, 3, 30))
        
    with pytest.raises(ValueError):
        sub_goal_A.add_subgoal(sub_goal_AB)
            
    sub_goal_AB = Goal("Subgoal AB", "this is a dummy goal", datetime(2025, 10, 1), datetime(2027, 3, 30))
        
    with pytest.raises(ValueError):
        sub_goal_A.add_subgoal(sub_goal_AB)

def test_get_completion_status():
    goal = Goal("Root Goal", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3), datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3))
    assert goal.get_completion_status() == 0
        
    sub_goal_A = Goal("Subgoal A", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 3, 30), datetime(2025, 10, 1, 2), datetime(2026, 3, 30))
    goal.add_subgoal(sub_goal_A)
    assert goal.get_completion_status() == 0
        
    goal.complete_subgoal_by_index(0)
    assert goal.get_completion_status() == 1
        
def test_get_num_subgoals(dummy_goal: Goal):
    goal = Goal("Root Goal", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3), datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3))
    assert goal.get_num_subgoals() == 0
        
    assert dummy_goal.get_num_subgoals() == 7

def test_get_subgoal():
    goal = Goal("Root Goal", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3), datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3))        
    sub_goal_A = Goal("Subgoal A", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 3, 30), datetime(2025, 10, 1, 2), datetime(2026, 3, 30))
    goal.add_subgoal(sub_goal_A)
        
    assert sub_goal_A == goal.get_subgoal_by_index(0)
    assert sub_goal_A == goal.get_subgoal_by_title("Subgoal A")
        
    sub_goal_AA = Goal("Subgoal AA", "Example text", datetime(2026, 2, 20), datetime(2026, 3, 30), datetime(2026, 2, 20), datetime(2026, 3, 30))
    sub_goal_A.add_subgoal(sub_goal_AA)
        
    assert sub_goal_AA == goal.get_subgoal_by_index(0).get_subgoal_by_index(0)
    assert sub_goal_AA == goal.get_subgoal_by_title("Subgoal A").get_subgoal_by_title("Subgoal AA")
    
def test_get_subgoal_invalid():
    goal = Goal("Root Goal", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3), datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3))        
        
    with pytest.raises(ValueError):
        goal.get_subgoal_by_title("Anything")
            
    sub_goal_A = Goal("Subgoal A", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 3, 30), datetime(2025, 10, 1, 2), datetime(2026, 3, 30))
    goal.add_subgoal(sub_goal_A)
        
    with pytest.raises(ValueError):
        goal.get_subgoal_by_title("Subgoal B")
            
    with pytest.raises(IndexError):
        goal.get_subgoal_by_index(100)
                
def test_get_subgoals():
    goal = Goal("Root Goal", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3), datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3))        
        
    goalList = []
        
    assert goalList ==  goal.get_subgoals()
        
    sub_goal_A = Goal("Subgoal A", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 3, 30), datetime(2025, 10, 1, 2), datetime(2026, 3, 30))
    sub_goal_AA = Goal("Subgoal AA", "Example text", datetime(2026, 2, 20), datetime(2026, 3, 30), datetime(2026, 2, 20), datetime(2026, 3, 30))

    goal.add_subgoal(sub_goal_A)
    goal.add_subgoal(sub_goal_AA)
        
    goalList.extend([sub_goal_A, sub_goal_AA])
    
    assert goalList == goal.get_subgoals()

def test_set_completed(dummy_goal: Goal):
    subgoal_A = dummy_goal.get_subgoal_by_title("Subgoal A")
    subgoal_A.set_completed()
        
    assert dummy_goal.get_completion_status() == 2
        
    dummy_goal.set_completed()
        
    assert dummy_goal.get_completion_status() == 8
    
def test_remove_subgoal(dummy_goal: Goal):
    dummy_goal.remove_subgoal_by_title("Subgoal A")
        
    assert dummy_goal.get_num_subgoals() == 5
        
def test_remove_subgoal_invalid():
    goal = Goal("Root Goal", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3), datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3))        
        
    with pytest.raises(ValueError):
        goal.remove_subgoal_by_title("Anything")
            
    sub_goal_A = Goal("Subgoal A", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 3, 30), datetime(2025, 10, 1, 2), datetime(2026, 3, 30))
    goal.add_subgoal(sub_goal_A)
        
    with pytest.raises(ValueError):
        goal.remove_subgoal_by_title("Subgoal B")
            
    with pytest.raises(IndexError):
        goal.remove_subgoal_by_index(100)
 
def test_complete_subgoal(dummy_goal: Goal):
    dummy_goal.complete_subgoal_by_title("Subgoal A")
    assert dummy_goal.get_completion_status() == 2
        
    dummy_goal.complete_subgoal_by_title("Subgoal B")
    assert dummy_goal.get_num_subgoals() == 7

def test_complete_subgoal_invalid_inputs():
    goal = Goal("Root Goal", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3), datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3))        
        
    with pytest.raises(ValueError):
        goal.complete_subgoal_by_title("Anything")
            
    sub_goal_A = Goal("Subgoal A", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 3, 30), datetime(2025, 10, 1, 2), datetime(2026, 3, 30))
    goal.add_subgoal(sub_goal_A)
        
    with pytest.raises(ValueError):
        goal.complete_subgoal_by_title("Subgoal B")
            
    with pytest.raises(IndexError):
        goal.remove_subgoal_by_index(100)
        
def test_get_progress_fraction(dummy_goal: Goal):
    goal = Goal("Root Goal", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3), datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3))
    assert "0/0" == goal.get_progress_fraction()
        
    dummy_goal.complete_subgoal_by_title("Subgoal A")
    assert "2/7" == dummy_goal.get_progress_fraction()
        
def test_get_progress_percent(dummy_goal: Goal):
    goal = Goal("Root Goal", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3), datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3))
    assert 100.0 == goal.get_progress_percent()
        
    dummy_goal.complete_subgoal_by_title("Subgoal A")
    assert 28.57142857142857 == dummy_goal.get_progress_percent()

def test_to_dict(dummy_goal: Goal):
    expected = {'_type': 'Goal', '_title': 'Root Goal', '_description': 'Example text', '_completed': False, '_deadline': '2026-10-01T03:00:00', '_start_date': '2025-10-01T02:00:00', '_end_date': '2026-10-01T03:00:00', '_startline': '2025-10-01T02:00:00', '_schedule_intervals': [{'start_date': '2025-10-01T02:00:00', 'end_date': '2026-10-01T03:00:00'}], '_completed_steps': 0, '_subgoals': [{'_type': 'TemporalTask', '_title': 'Dummy Temporal Task', '_description': 'Example text', '_completed': False, '_deadline': None, '_start_date': '2025-10-10T00:00:00', '_end_date': '2025-10-17T00:00:00', '_startline': None, '_schedule_intervals': [{'start_date': '2025-10-10T00:00:00', 'end_date': '2025-10-17T00:00:00'}]}, {'_type': 'Goal', '_title': 'Subgoal A', '_description': 'Example text', '_completed': False, '_deadline': '2026-03-30T00:00:00', '_start_date': '2025-10-01T02:00:00', '_end_date': '2026-03-30T00:00:00', '_startline': '2025-10-01T02:00:00', '_schedule_intervals': [{'start_date': '2025-10-01T02:00:00', 'end_date': '2026-03-30T00:00:00'}], '_completed_steps': 0, '_subgoals': [{'_type': 'Goal', '_title': 'Subgoal AA', '_description': 'Example text', '_completed': False, '_deadline': '2025-12-30T00:00:00', '_start_date': '2025-10-01T02:00:00', '_end_date': '2025-12-30T00:00:00', '_startline': '2025-10-01T02:00:00', '_schedule_intervals': [{'start_date': '2025-10-01T02:00:00', 'end_date': '2025-12-30T00:00:00'}], '_completed_steps': 0, '_subgoals': []}]}, {'_type': 'Goal', '_title': 'Subgoal B', '_description': 'Example text', '_completed': False, '_deadline': '2026-10-01T02:00:00', '_start_date': '2026-03-30T00:00:00', '_end_date': '2026-10-01T02:00:00', '_startline': '2026-03-30T00:00:00', '_schedule_intervals': [{'start_date': '2026-03-30T00:00:00', 'end_date': '2026-10-01T02:00:00'}], '_completed_steps': 0, '_subgoals': [{'_type': 'Goal', '_title': 'Subgoal BA', '_description': 'Example text', '_completed': False, '_deadline': '2026-05-01T00:00:00', '_start_date': '2026-03-30T00:00:00', '_end_date': '2026-05-01T00:00:00', '_startline': '2026-03-30T00:00:00', '_schedule_intervals': [{'start_date': '2026-03-30T00:00:00', 'end_date': '2026-05-01T00:00:00'}], '_completed_steps': 0, '_subgoals': []}, {'_type': 'Goal', '_title': 'Subgoal BB', '_description': 'Example text', '_completed': False, '_deadline': '2026-10-01T00:00:00', '_start_date': '2026-05-01T00:00:00', '_end_date': '2026-10-01T00:00:00', '_startline': '2026-05-01T00:00:00', '_schedule_intervals': [{'start_date': '2026-05-01T00:00:00', 'end_date': '2026-10-01T00:00:00'}], '_completed_steps': 0, '_subgoals': []}, {'_type': 'Task', '_title': 'Task', '_description': 'Example text', '_completed': False, '_deadline': '2026-05-01T00:00:00'}]}]}
    
    assert expected == dummy_goal.to_dict()
    
def test_from_dict(dummy_goal: Goal):
    json = {'_type': 'Goal', '_title': 'Root Goal', '_description': 'Example text', '_completed': False, '_deadline': '2026-10-01T03:00:00', '_start_date': '2025-10-01T02:00:00', '_end_date': '2026-10-01T03:00:00', '_startline': '2025-10-01T02:00:00', '_schedule_intervals': [{'start_date': '2025-10-01T02:00:00', 'end_date': '2026-10-01T03:00:00'}], '_completed_steps': 0, '_subgoals': [{'_type': 'TemporalTask', '_title': 'Dummy Temporal Task', '_description': 'Example text', '_completed': False, '_deadline': None, '_start_date': '2025-10-10T00:00:00', '_end_date': '2025-10-17T00:00:00', '_startline': None, '_schedule_intervals': [{'start_date': '2025-10-10T00:00:00', 'end_date': '2025-10-17T00:00:00'}]}, {'_type': 'Goal', '_title': 'Subgoal A', '_description': 'Example text', '_completed': False, '_deadline': '2026-03-30T00:00:00', '_start_date': '2025-10-01T02:00:00', '_end_date': '2026-03-30T00:00:00', '_startline': '2025-10-01T02:00:00', '_schedule_intervals': [{'start_date': '2025-10-01T02:00:00', 'end_date': '2026-03-30T00:00:00'}], '_completed_steps': 0, '_subgoals': [{'_type': 'Goal', '_title': 'Subgoal AA', '_description': 'Example text', '_completed': False, '_deadline': '2025-12-30T00:00:00', '_start_date': '2025-10-01T02:00:00', '_end_date': '2025-12-30T00:00:00', '_startline': '2025-10-01T02:00:00', '_schedule_intervals': [{'start_date': '2025-10-01T02:00:00', 'end_date': '2025-12-30T00:00:00'}], '_completed_steps': 0, '_subgoals': []}]}, {'_type': 'Goal', '_title': 'Subgoal B', '_description': 'Example text', '_completed': False, '_deadline': '2026-10-01T02:00:00', '_start_date': '2026-03-30T00:00:00', '_end_date': '2026-10-01T02:00:00', '_startline': '2026-03-30T00:00:00', '_schedule_intervals': [{'start_date': '2026-03-30T00:00:00', 'end_date': '2026-10-01T02:00:00'}], '_completed_steps': 0, '_subgoals': [{'_type': 'Goal', '_title': 'Subgoal BA', '_description': 'Example text', '_completed': False, '_deadline': '2026-05-01T00:00:00', '_start_date': '2026-03-30T00:00:00', '_end_date': '2026-05-01T00:00:00', '_startline': '2026-03-30T00:00:00', '_schedule_intervals': [{'start_date': '2026-03-30T00:00:00', 'end_date': '2026-05-01T00:00:00'}], '_completed_steps': 0, '_subgoals': []}, {'_type': 'Goal', '_title': 'Subgoal BB', '_description': 'Example text', '_completed': False, '_deadline': '2026-10-01T00:00:00', '_start_date': '2026-05-01T00:00:00', '_end_date': '2026-10-01T00:00:00', '_startline': '2026-05-01T00:00:00', '_schedule_intervals': [{'start_date': '2026-05-01T00:00:00', 'end_date': '2026-10-01T00:00:00'}], '_completed_steps': 0, '_subgoals': []}, {'_type': 'Task', '_title': 'Task', '_description': 'Example text', '_completed': False, '_deadline': '2026-05-01T00:00:00'}]}]}
    goal = Goal.from_dict(json)
    
    assert goal == dummy_goal