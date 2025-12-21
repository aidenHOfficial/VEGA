import unittest
from models import *
from datetime import datetime, timedelta
from models.time_interval import TimeInterval
from models.task import Task
from models.temporal_task import TemporalTask
from models.goal import Goal
from models.routine import Routine
from models.event import Event
from models.time_tree_node import TimeTreeNode
from models.time_tree import TimeTree
from models.calendar import Calendar

print("\n\n")

class TimeIntervalTests(unittest.TestCase):
    def test___init__(self):
        self.assertIsNotNone(TimeInterval(datetime(2004, 10, 1), datetime(2004, 10, 2)))

    def test___init___invalid(self):
        with self.assertRaises(ValueError):
            interval = TimeInterval(datetime(2004, 11, 1), datetime(2004, 10, 2))
    
    def test_get_start_date(self):
        interval = TimeInterval(datetime(2004, 10, 1), datetime(2004, 10, 2))
        self.assertEqual(datetime(2004, 10, 1), interval.get_start_date())
        self.assertEqual(datetime(2004, 10, 1), interval.start_date)

    def test_get_end_date(self):
        interval = TimeInterval(datetime(2004, 10, 1), datetime(2004, 10, 2))
        self.assertEqual(datetime(2004, 10, 2), interval.get_end_date())
        self.assertEqual(datetime(2004, 10, 2), interval.end_date)

    def test_get_interval(self):
        interval = TimeInterval(datetime(2004, 10, 1), datetime(2004, 10, 2))
        self.assertEqual((datetime(2004, 10, 1), datetime(2004, 10, 2)), interval.get_interval())
     
    def test_get_duration(self):   
        # TODO: Create a test for the get_duration function
        pass
    
class TaskTests(unittest.TestCase):
    def test_failed_constructor(self):
        task = Task("this is a test task", datetime(2004,1,1))
        self.assertIsNotNone(task)

    def test_constructor_with_deadline(self):
        task = Task("test", "this is a test task", datetime(2004,1,1))
        self.assertIsNotNone(task)

    def test_constructor_without_deadline(self):
        task = Task("test", "this is a test task")
        self.assertIsNotNone(task)
    
    def test_get_completion_status(self):
        task = Task("test", "this is a test task")
        self.assertFalse(task.get_completion_status())

        task._completed = True
        self.assertTrue(task.get_completion_status())

    def test_get_title(self):
        task = Task("test", "this is a test task")
        self.assertEqual(task.get_title(), f"test")

        task_complicated_title = Task("27hsiae7ifkiashie", "this is a test task")
        self.assertEqual(task_complicated_title.get_title(), f"27hsiae7ifkiashie")

    def test_get_description(self):
        task = Task("test", "this is a test task")
        self.assertEqual(task.get_description(), f"this is a test task")

        task_complicated_description = Task("test", "Aidsiojfeisoi8398urwnflkdjs")
        self.assertEqual(task_complicated_description.get_description(), f"Aidsiojfeisoi8398urwnflkdjs")

    def test_get_deadline_with_set_deadline(self):
        task = Task("test", "this is a test task", datetime(2004, 10, 1))
        self.assertEqual(task.get_deadline(), datetime(2004, 10, 1))

    def test_get_deadline_with_no_deadline(self):
        task = Task("test", "this is a test task")
        self.assertEqual(task.get_deadline(), None)

class TemporalTaskTests(unittest.TestCase):
    def test_constructor_with_invalid_dates(self):
        with self.assertRaises(ValueError):
            TemporalTask("test", "this is a test task", datetime(2025, 10, 1), datetime(2020, 10, 1))

    def test_constructor_with_out_of_scope_lines(self):
        with self.assertRaises(ValueError):
            TemporalTask("test", "this is a test task", datetime(2025, 9, 1), datetime(2025, 10, 2), datetime(2025, 9, 2), datetime(2025, 10, 2))
        
        with self.assertRaises(ValueError):
            TemporalTask("test", "this is a test task", datetime(2025, 9, 1), datetime(2025, 10, 2), startline=datetime(2025, 9, 2))

        with self.assertRaises(ValueError):
            TemporalTask("test", "this is a test task", datetime(2025, 9, 2), datetime(2025, 10, 2), deadline=datetime(2025, 10, 1))
    
        reschedules = [TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)), TimeInterval(datetime(2025, 10, 3), datetime(2025, 10, 4))]
        with self.assertRaises(ValueError):
            TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10), deadline=datetime(2025, 10, 9), schedule_intervals=reschedules)
        
        with self.assertRaises(ValueError):
            TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10), startline=datetime(2025, 10, 2), schedule_intervals=reschedules)

    def test_get_start_date(self):
        task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10))
        self.assertEqual(task.get_start_date(), datetime(2025, 10, 2))

    def test_get_end_date(self):
        task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10))
        self.assertEqual(task.get_end_date(), datetime(2025, 10, 10))
    
    def test_get_startline(self):
        task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10), datetime(2025, 10, 2))
        self.assertEqual(task.get_startline(), datetime(2025, 10, 2))

    def test_get_total_time(self):
        task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10))
        self.assertEqual(task.get_total_time(), datetime(2025, 10, 10) - datetime(2025, 10, 2))

    def test_get_time_slot(self):
        task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10))
        self.assertEqual(task.get_time_slot(), TimeInterval(datetime(2025, 10, 2), datetime(2025, 10, 10)))

    def test_get_schedule_interval_no_values(self):
        task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10))
        self.assertEqual(task.get_schedule_intervals(), [TimeInterval(datetime(2025, 10, 2), datetime(2025, 10, 10))])

    def test_get_schedule_interval_with_values(self):
        task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10), schedule_intervals=[TimeInterval(datetime(2025, 10, 3), datetime(2025, 10, 11))])
        self.assertEqual(task.get_schedule_intervals(), [TimeInterval(datetime(2025, 10, 2), datetime(2025, 10, 11))])

    def test_get_duration(self):
        # TODO: add a test for the get_duration function
        pass

    def test_add_schedule_interval(self):
        task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10))
        task.add_schedule_interval(TimeInterval(datetime(2025, 10, 3), datetime(2025, 10, 11)))
        self.assertEqual(task.get_schedule_intervals(), [TimeInterval(datetime(2025, 10, 2), datetime(2025, 10, 11))])
        
        task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10), datetime(2025, 10, 2), datetime(2025, 10, 10))
        task.add_schedule_interval(TimeInterval(datetime(2025, 10, 2), datetime(2025, 10, 10)))
        self.assertEqual(task.get_schedule_intervals(), [TimeInterval(datetime(2025, 10, 2), datetime(2025, 10, 10))])
        
    def test_add_schedule_interval_invalid_values(self):
        task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10), datetime(2025, 10, 2), datetime(2025, 10, 10))
        with self.assertRaises(ValueError):
            self.assertRaises(ValueError, task.add_schedule_interval(TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 10))))
        with self.assertRaises(ValueError):
            self.assertRaises(ValueError, task.add_schedule_interval(TimeInterval(datetime(2025, 10, 2), datetime(2025, 10, 12))))

class GoalTests(unittest.TestCase):
    def get_dummy_goal(self):
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
    
    # def test_print_goal(self):
    #     print(self.get_dummy_goal())
    
    def test_add_subgoal(self):
        goal = self.get_dummy_goal()
        
        sub_goal_A = goal.get_subgoal("Subgoal A")
        sub_goal_AB = Goal("Subgoal AB", "this is a dummy goal", datetime(2025, 10, 1, 2), datetime(2026, 3, 30))
        sub_goal_A.add_subgoal(sub_goal_AB)
        
        self.assertEqual(sub_goal_AB, goal.get_subgoal("Subgoal A").get_subgoal("Subgoal AB"))
       
    def test_add_subgoal_invalid(self):
        goal = self.get_dummy_goal()
        
        sub_goal_A = goal.get_subgoal("Subgoal A")
        sub_goal_AB = Goal("Subgoal AB", "this is a dummy goal", datetime(2024, 10, 1), datetime(2026, 3, 30))
        
        with self.assertRaises(ValueError):
            sub_goal_A.add_subgoal(sub_goal_AB)
            
        sub_goal_AB = Goal("Subgoal AB", "this is a dummy goal", datetime(2025, 10, 1), datetime(2027, 3, 30))
        
        with self.assertRaises(ValueError):
            sub_goal_A.add_subgoal(sub_goal_AB)
         
    def test_complete_subgoal(self):
        goal = self.get_dummy_goal()
        goal.complete_subgoal("Subgoal A")
        self.assertEqual(goal.get_completion_status(), 2)
        
    def test_get_completion_status(self):
        goal = Goal("Root Goal", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3), datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3))
        self.assertEqual(goal.get_completion_status(), 0)
        
        sub_goal_A = Goal("Subgoal A", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 3, 30), datetime(2025, 10, 1, 2), datetime(2026, 3, 30))
        goal.add_subgoal(sub_goal_A)
        self.assertEqual(goal.get_completion_status(), 0)
        
        goal.complete_subgoal(0)
        self.assertEqual(goal.get_completion_status(), 1)
        
    def test_get_num_subgoals(self):
        goal = Goal("Root Goal", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3), datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3))
        self.assertEqual(goal.get_num_subgoals(), 0)
        
        goal = self.get_dummy_goal()
        self.assertEqual(goal.get_num_subgoals(), 7)

    def test_get_subgoal(self):
        goal = Goal("Root Goal", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3), datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3))        
        sub_goal_A = Goal("Subgoal A", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 3, 30), datetime(2025, 10, 1, 2), datetime(2026, 3, 30))
        goal.add_subgoal(sub_goal_A)
        
        self.assertEqual(sub_goal_A, goal.get_subgoal(0))
        self.assertEqual(sub_goal_A, goal.get_subgoal("Subgoal A"))
        
        sub_goal_AA = Goal("Subgoal AA", "Example text", datetime(2026, 2, 20), datetime(2026, 3, 30), datetime(2026, 2, 20), datetime(2026, 3, 30))
        sub_goal_A.add_subgoal(sub_goal_AA)
        
        self.assertEqual(sub_goal_AA, goal.get_subgoal(0).get_subgoal(0))
        self.assertEqual(sub_goal_AA, goal.get_subgoal("Subgoal A").get_subgoal("Subgoal AA"))
    
    def test_get_subgoal_invalid(self):
        goal = Goal("Root Goal", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3), datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3))        
        
        with self.assertRaises(ValueError):
            goal.get_subgoal("Anything")
            
        sub_goal_A = Goal("Subgoal A", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 3, 30), datetime(2025, 10, 1, 2), datetime(2026, 3, 30))
        goal.add_subgoal(sub_goal_A)
        
        with self.assertRaises(ValueError):
            goal.get_subgoal("Subgoal B")
            
        with self.assertRaises(IndexError):
            goal.get_subgoal(100)
        
        with self.assertRaises(TypeError):
            goal.get_subgoal(datetime(2004, 10, 1))
                
    def test_get_subgoals(self):
        goal = Goal("Root Goal", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3), datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3))        
        
        goalList = []
        
        self.assertEqual(goalList, goal.get_subgoals())
        
        sub_goal_A = Goal("Subgoal A", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 3, 30), datetime(2025, 10, 1, 2), datetime(2026, 3, 30))
        sub_goal_AA = Goal("Subgoal AA", "Example text", datetime(2026, 2, 20), datetime(2026, 3, 30), datetime(2026, 2, 20), datetime(2026, 3, 30))

        goal.add_subgoal(sub_goal_A)
        goal.add_subgoal(sub_goal_AA)
        
        goalList.extend([sub_goal_A, sub_goal_AA])
                
        self.assertEqual(goalList, goal.get_subgoals())

    def test_set_completed(self):
        goal = self.get_dummy_goal()
        
        subgoal_A = goal.get_subgoal("Subgoal A")
        subgoal_A.set_completed()
        
        self.assertEqual(2, goal.get_completion_status())
        
        goal.set_completed()
        
        self.assertEqual(8, goal.get_completion_status())
    
    def test_remove_subgoal(self):
        goal = self.get_dummy_goal()
        goal.remove_subgoal("Subgoal A")
        
        self.assertEqual(5, goal.get_num_subgoals())
        
        goal = self.get_dummy_goal()
        goal.remove_subgoal(0)
        
        self.assertEqual(7, goal.get_num_subgoals())
        
    def test_remove_subgoal_invalid(self):
        goal = Goal("Root Goal", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3), datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3))        
        
        with self.assertRaises(ValueError):
            goal.remove_subgoal("Anything")
            
        sub_goal_A = Goal("Subgoal A", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 3, 30), datetime(2025, 10, 1, 2), datetime(2026, 3, 30))
        goal.add_subgoal(sub_goal_A)
        
        with self.assertRaises(ValueError):
            goal.remove_subgoal("Subgoal B")
            
        with self.assertRaises(IndexError):
            goal.remove_subgoal(100)
        
        with self.assertRaises(TypeError):
            goal.remove_subgoal(datetime(2004, 10, 1))
 
    def test_complete_subgoal(self):
        goal = self.get_dummy_goal()
        goal.complete_subgoal("Subgoal A")
        self.assertEqual(2, goal.get_completion_status())
        
        goal.complete_subgoal("Subgoal B")
        self.assertEqual(7, goal.get_num_subgoals())
        
        goal = self.get_dummy_goal()
        goal.complete_subgoal(1)
        self.assertEqual(2, goal.get_completion_status())
        
        goal.complete_subgoal(2)
        self.assertEqual(7, goal.get_num_subgoals())
        
    def test_complete_subgoal(self):
        goal = Goal("Root Goal", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3), datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3))        
        
        with self.assertRaises(ValueError):
            goal.complete_subgoal("Anything")
            
        sub_goal_A = Goal("Subgoal A", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 3, 30), datetime(2025, 10, 1, 2), datetime(2026, 3, 30))
        goal.add_subgoal(sub_goal_A)
        
        with self.assertRaises(ValueError):
            goal.remove_subgoal("Subgoal B")
            
        with self.assertRaises(IndexError):
            goal.remove_subgoal(100)
        
        with self.assertRaises(TypeError):
            goal.remove_subgoal(datetime(2004, 10, 1))
        
    def test_get_progress_fraction(self):
        goal = Goal("Root Goal", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3), datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3))        
        self.assertEqual(f"0/0", goal.get_progress_fraction())
        
        goal = self.get_dummy_goal()
        goal.complete_subgoal("Subgoal A")
        self.assertEqual(f"2/7", goal.get_progress_fraction())
        
    def test_get_progress_percent(self):
        goal = Goal("Root Goal", "Example text", datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3), datetime(2025, 10, 1, 2), datetime(2026, 10, 1, 3))        
        self.assertEqual(100.0, goal.get_progress_percent())
        
        goal = self.get_dummy_goal()
        goal.complete_subgoal("Subgoal A")
        self.assertAlmostEqual(28.57142857142857, goal.get_progress_percent())

class RoutineTests(unittest.TestCase):    
    def test_add_task(self):
        routine = Routine("Routine", "Example text", datetime(2025, 1, 1), datetime(2025, 1, 2))
        
        temp_task = TemporalTask("Task A", "Example text", datetime(2025, 1, 1, 8), datetime(2025, 1, 1, 10))
        routine.add_task(temp_task)
        self.assertIn(temp_task, routine._tasks)

        non_temp_task = Task("Task B", "Example Text")
        routine.add_task(non_temp_task, timedelta(hours=1))
        self.assertIn(non_temp_task, routine._tasks)
        
    def test_add_task_invalid(self):
        routine = Routine("Routine", "Example text", datetime(2025, 1, 1), datetime(2025, 1, 2))
        
        non_temp_task = Task("Task A", "No complete time provided")
        with self.assertRaises(ValueError):
            routine.add_task(non_temp_task)
            
        with self.assertRaises(ValueError):
            routine.add_task(non_temp_task, 0)
    
    def test_get_tasks(self):
        check_list = []
        
        routine = Routine("Routine", "Example text", datetime(2025, 1, 1, 2), datetime(2025, 1, 2))
        
        self.assertEqual(check_list, routine.get_tasks())
        
        task_A = Task("Task A", "Example text")
        task_B = TemporalTask("Task B", "Example text", datetime(2025, 1, 1, 2), datetime(2025, 1, 1, 3))
        
        routine.add_task(task_A, timedelta(10))
        routine.add_task(task_B)
        
        check_list.extend([task_A, task_B])
                
        for item in routine.get_tasks():
            self.assertIn(item, check_list)
          
    def test_get_task(self):
        routine = Routine("Routine", "Example text", datetime(2025, 1, 1), datetime(2025, 1, 2))
                
        task_A = Task("Task A", "Example text")
        task_B = TemporalTask("Task B", "Example text", datetime(2025, 1, 1, 2), datetime(2025, 1, 1, 3))
        
        routine.add_task(task_A, timedelta(10))
        routine.add_task(task_B)
        
        self.assertEqual(task_A, routine.get_task(0))
        self.assertEqual(task_B, routine.get_task(1))
        self.assertEqual(task_A, routine.get_task("Task A"))
        self.assertEqual(task_B, routine.get_task("Task B"))
        
    def test_get_task_invalid(self):
        routine = Routine("Routine", "Example text", datetime(2025, 1, 1), datetime(2025, 1, 2))
        
        with self.assertRaises(IndexError):
            routine.get_task(0)
        with self.assertRaises(ValueError):
            routine.get_task("Anything")
                
        task_A = Task("Task A", "Example text")
        task_B = TemporalTask("Task B", "Example text", datetime(2025, 1, 1, 2), datetime(2025, 1, 1, 3))
        
        routine.add_task(task_A, timedelta(10))
        routine.add_task(task_B)
        
        with self.assertRaises(IndexError):
            routine.get_task(-1)
        with self.assertRaises(IndexError):
            routine.get_task(1000)
        with self.assertRaises(TypeError):
            routine.get_task(datetime(2004, 10, 1))
        with self.assertRaises(ValueError):
            routine.get_task("Anything")
            
    def test_get_task_complete_time(self):
        routine = Routine("Routine", "Example text", datetime(2025, 1, 1), datetime(2025, 1, 2))
                
        task_A = Task("Task A", "Example text")
        task_B = TemporalTask("Task B", "Example text", datetime(2025, 1, 1, 2), datetime(2025, 1, 1, 3))
        
        routine.add_task(task_A, timedelta(10))
        routine.add_task(task_B)
        
        self.assertEqual(timedelta(10), routine.get_task_complete_time(0))
        self.assertEqual(task_B.get_total_time(), routine.get_task_complete_time(1))
        self.assertEqual(timedelta(10), routine.get_task_complete_time("Task A"))
        self.assertEqual(task_B.get_total_time(), routine.get_task_complete_time("Task B"))
        
    def test_get_task_complete_time_invalid(self):
        routine = Routine("Routine", "Example text", datetime(2025, 1, 1), datetime(2025, 1, 2))
        
        with self.assertRaises(IndexError):
            routine.get_task_complete_time(0)
        with self.assertRaises(ValueError):
            routine.get_task_complete_time("Anything")
                
        task_A = Task("Task A", "Example text")
        task_B = TemporalTask("Task B", "Example text", datetime(2025, 1, 1, 2), datetime(2025, 1, 1, 3))
        
        routine.add_task(task_A, timedelta(10))
        routine.add_task(task_B)
        
        with self.assertRaises(IndexError):
            routine.get_task_complete_time(-1)
        with self.assertRaises(IndexError):
            routine.get_task_complete_time(1000)
        with self.assertRaises(TypeError):
            routine.get_task_complete_time(datetime(2004, 10, 1))
        with self.assertRaises(ValueError):
            routine.get_task_complete_time("Anything")
            
    def test_get_estimated_time(self):
        routine = Routine("Routine", "Example text", datetime(2025, 1, 1, 2, 0), datetime(2025, 1, 1, 3, 0))
        
        self.assertEqual(routine.get_estimated_time(), timedelta(0, 0))
        self.assertEqual(routine.total_estimated_time, timedelta(0, 0))
                
        task_A = Task("Task A", "Example text")
        task_B = TemporalTask("Task B", "Example text", datetime(2025, 10, 1, 2), datetime(2025, 10, 1, 3))
        
        routine.add_task(task_A, timedelta(0, 0, 0, 0, 30, 0, 0))
        routine.add_task(task_B)
        
        self.assertEqual(routine.get_estimated_time(), (timedelta(0, 0, 0, 0, 30, 0, 0) + (datetime(2025, 10, 1, 3) - datetime(2025, 10, 1, 2))))
        self.assertEqual(routine.total_estimated_time, (timedelta(0, 0, 0, 0, 30, 0, 0) + (datetime(2025, 10, 1, 3) - datetime(2025, 10, 1, 2))))
        
    def test_remove_task(self):
        routine = Routine("Routine", "Example text", datetime(2025, 1, 1, 2, 0), datetime(2025, 1, 1, 3, 0))
                        
        task_A = Task("Task A", "Example text")
        task_B = TemporalTask("Task B", "Example text", datetime(2025, 10, 1, 2), datetime(2025, 10, 1, 3))
        
        routine.add_task(task_A, timedelta(0, 0, 0, 0, 30, 0, 0))
        routine.add_task(task_B)
        
        routine.remove_task(0)
        
        tasks = routine.get_tasks()
        for task in tasks:
            self.assertNotEqual(task, task_A)
            
        routine.remove_task("Task B")
        
        tasks = routine.get_tasks()
        for task in tasks:
            self.assertNotEqual(task, task_A)
            self.assertNotEqual(task, task_B)
            
    def test_remove_task_invalid(self):
        routine = Routine("Routine", "Example text", datetime(2025, 1, 1, 2, 0), datetime(2025, 1, 1, 3, 0))
        
        with self.assertRaises(IndexError):
            routine.remove_task(0)
        with self.assertRaises(ValueError):
            routine.remove_task("asdf")
                        
        task_A = Task("Task A", "Example text")
        task_B = TemporalTask("Task B", "Example text", datetime(2025, 10, 1, 2), datetime(2025, 10, 1, 3))
        
        routine.add_task(task_A, timedelta(0, 0, 0, 0, 30, 0, 0))
        routine.add_task(task_B)
   
        with self.assertRaises(ValueError):
            routine.remove_task("Task C")
        with self.assertRaises(IndexError):
            routine.remove_task(1000)
        with self.assertRaises(IndexError):
            routine.remove_task(-1)
        with self.assertRaises(TypeError):
            routine.remove_task(datetime(0))
        
    def test_change_order(self):
        routine = Routine("Routine", "Example text", datetime(2025, 1, 1, 2, 0), datetime(2025, 1, 1, 3, 0))
        task_A = Task("Task A", "Example text")
        task_B = TemporalTask("Task B", "Example text", datetime(2025, 10, 1, 2), datetime(2025, 10, 1, 3))
        routine.add_task(task_A, timedelta(0, 0, 0, 0, 30, 0, 0))
        routine.add_task(task_B)
        
        reorder = [task_B, task_A]
        
        routine.change_order(reorder)
        
        self.assertEqual(reorder, routine.get_tasks())
        
    def test_change_order_invalid(self):
        routine = Routine("Routine", "Example text", datetime(2025, 1, 1, 2, 0), datetime(2025, 1, 1, 3, 0))
        task_A = Task("Task A", "Example text")
        task_B = TemporalTask("Task B", "Example text", datetime(2025, 10, 1, 2), datetime(2025, 10, 1, 3))
        routine.add_task(task_A, timedelta(0, 0, 0, 0, 30, 0, 0))
        routine.add_task(task_B)
        
        
        reorder = [task_B]
        
        with self.assertRaises(ValueError):
            routine.change_order(reorder)
        
        task_C = Task("Task C", "Example text")
        
        reorder = [task_B, task_A, task_C]
        
        with self.assertRaises(ValueError):
            routine.change_order(reorder)
        
    def test_change_task_complete_time(self):
        routine = Routine("Routine", "Example text", datetime(2025, 1, 1, 2, 0), datetime(2025, 1, 1, 3, 0))
        
        task_A = Task("Task A", "Example text")
        task_B = TemporalTask("Task B", "Example text", datetime(2025, 10, 1, 2), datetime(2025, 10, 1, 3))
        
        routine.add_task(task_A, timedelta(0, 0, 0, 0, 30, 0, 0))
        routine.add_task(task_B)
        
        routine.change_task_complete_time(0, timedelta(0, 0, 0, 0, 15, 0, 0))
        
        self.assertEqual(timedelta(0, 0, 0, 0, 15, 0, 0), routine.get_task_complete_time(0))
        
        routine.change_task_complete_time("Task A", timedelta(0, 0, 0, 0, 30, 0, 0))
        
        self.assertEqual(timedelta(0, 0, 0, 0, 30, 0, 0), routine.get_task_complete_time("Task A"))
        
    def test_change_task_complete_time_invalid(self):
        routine = Routine("Routine", "Example text", datetime(2025, 1, 1, 2, 0), datetime(2025, 1, 1, 3, 0))
                
        with self.assertRaises(IndexError):
            routine.change_task_complete_time(0, timedelta(0, 0, 0, 0, 15, 0, 0))
        with self.assertRaises(ValueError):
            routine.change_task_complete_time("asdf", timedelta(0, 0, 0, 0, 15, 0, 0))
        
        task_A = Task("Task A", "Example text")
        task_B = TemporalTask("Task B", "Example text", datetime(2025, 10, 1, 2), datetime(2025, 10, 1, 3))
        
        routine.add_task(task_A, timedelta(0, 0, 0, 0, 30, 0, 0))
        routine.add_task(task_B)
        
        routine.change_task_complete_time("Task A", timedelta(0, 0, 0, 0, 15, 0, 0))
        
        with self.assertRaises(ValueError):
            routine.change_task_complete_time("Task C", timedelta(0, 0, 0, 0, 30, 0, 0))
        with self.assertRaises(IndexError):
            routine.change_task_complete_time(1000, timedelta(0, 0, 0, 0, 30, 0, 0))
        with self.assertRaises(IndexError):
            routine.change_task_complete_time(-1, timedelta(0, 0, 0, 0, 30, 0, 0))
        with self.assertRaises(TypeError):
            routine.change_task_complete_time(datetime(0), timedelta(0, 0, 0, 0, 30, 0, 0))
    
    def test_get_next_time_slot(self):
        routine = Routine("Routine", "Example text", datetime(2025, 1, 1, 2, 0), datetime(2025, 1, 1, 3, 0))
        
        self.assertEqual(
            (datetime(2025, 1, 1, 2, 0) + timedelta(1), datetime(2025, 1, 1, 3, 0) + timedelta(1)),
            routine.get_next_time_slot(1)
        )
        
        self.assertEqual(
            (datetime(2025, 1, 1, 2, 0) + timedelta(2), datetime(2025, 1, 1, 3, 0) + timedelta(2)),
            routine.get_next_time_slot(2)
        )
        
        routine = Routine("Routine", "Example text", datetime(2025, 1, 1, 2, 0), datetime(2025, 1, 1, 3, 0), timedelta(0, 0, 0, 0, 0, 0, 1))
        
        self.assertEqual(
            (datetime(2025, 1, 1, 2, 0) + timedelta(0, 0, 0, 0, 0, 0, 1), datetime(2025, 1, 1, 3, 0) + timedelta(0, 0, 0, 0, 0, 0, 1)),
            routine.get_next_time_slot(1)
        )
        
        self.assertEqual(
            (datetime(2025, 1, 1, 2, 0) + timedelta(0, 0, 0, 0, 0, 0, 2), datetime(2025, 1, 1, 3, 0) + timedelta(0, 0, 0, 0, 0, 0, 2)),
            routine.get_next_time_slot(2)
        )
        
    def test_get_next_time_slot_invalid(self):
        routine = Routine("Routine", "Example text", datetime(2025, 1, 1, 2, 0), datetime(2025, 1, 1, 3, 0))
        
        with self.assertRaises(ValueError):
            routine.get_next_time_slot(0)
        with self.assertRaises(ValueError):
            routine.get_next_time_slot(-1)
        
        routine = Routine("Routine", "Example text", datetime(2025, 1, 1, 2, 0), datetime(2025, 1, 1, 3, 0), timedelta(0, 0, 0, 0, 0, 0, 1))
        
        with self.assertRaises(ValueError):
            routine.get_next_time_slot(0)
        with self.assertRaises(ValueError):
            routine.get_next_time_slot(-1)
        
class EventTests(unittest.TestCase):
    def test_get_priority_score_simple(self):
        task = Task("Make bed", "Remember after waking up to go to bed")
        temp_task = TemporalTask("Reminder", "Remind Jasmine to water her plants", datetime.now() + timedelta(0, 0, 0, 0, 5), datetime.now() + timedelta(0, 0, 0, 0, 10))

        task_event = Event(task, 10, 20, 10, 0)
        temp_task_event = Event(temp_task, 20, 15, 10, 25)

        task_event_priority = task_event.get_priority_score()
        temporal_task_event_priority = temp_task_event.get_priority_score()
        
        self.assertGreater(temporal_task_event_priority, task_event_priority)
    
    def test_get_priority_score_closer_deadline_results_in_higher_score(self):
        temp_task = TemporalTask("Reminder", "Test", datetime.now() + timedelta(0, 0, 0, 0, 5), datetime.now() + timedelta(0, 0, 0, 0, 10))
        temp_task_2 = TemporalTask("Reminder2", "Test2", datetime.now() + timedelta(0, 0, 0, 0, 6), datetime.now() + timedelta(0, 0, 0, 0, 11))

        temp_task_event = Event(temp_task, 20, 15, 10, 25)
        temp_task_event_2 = Event(temp_task_2, 20, 15, 10, 25)

        temporal_task_event_priority = temp_task_event.get_priority_score()
        temporal_task_event_priority_2 = temp_task_event_2.get_priority_score()
        
        self.assertGreater(temporal_task_event_priority, temporal_task_event_priority_2)
        
    def test_increase_value_results_in_higher_score(self):
        temp_task = TemporalTask("Reminder", "Test", datetime.now() + timedelta(0, 0, 0, 0, 5), datetime.now() + timedelta(0, 0, 0, 0, 10))
        temp_task_2 = TemporalTask("Reminder", "Test", datetime.now() + timedelta(0, 0, 0, 0, 5), datetime.now() + timedelta(0, 0, 0, 0, 10))
        
        values_list = [20, 15, 10, 24]
        
        for i in range(len(values_list)):
            new_values = values_list.copy()
            new_values[i] += 1
            
            temp_task_event = Event(temp_task, *new_values)
            temp_task_event_2 = Event(temp_task, *values_list)
            
            temporal_task_event_priority = temp_task_event.get_priority_score()
            temporal_task_event_priority_2 = temp_task_event_2.get_priority_score()
            
            self.assertGreater(temporal_task_event_priority, temporal_task_event_priority_2)
            
    def test_get_task(self):
        task = Task("Make bed", "Remember after waking up to go to bed")
        temp_task = TemporalTask("Reminder", "Remind Jasmine to water her plants", datetime.now() + timedelta(0, 0, 0, 0, 5), datetime.now() + timedelta(0, 0, 0, 0, 10))

        task_event = Event(task, 10, 20, 10, 0)
        temp_task_event = Event(temp_task, 20, 15, 10, 25)
        
        self.assertEqual(task_event.get_task(), task)
        self.assertEqual(temp_task_event.get_task(), temp_task)
        
    def test_get_deadline(self):
        task = Task("Make bed", "Remember after waking up to go to bed")
        task_2 = Task("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1))

        task_event = Event(task, 10, 20, 10, 0)
        temp_task_event = Event(task_2, 20, 15, 10, 25)
        
        self.assertEqual(task_event.get_deadline(), None)
        self.assertEqual(temp_task_event.get_deadline(), datetime(2025, 10, 1))
        
    def test_get_startline(self):
        temp_task = TemporalTask("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1), datetime(2025, 10, 2))
        temp_task_2 = TemporalTask("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1), datetime(2025, 10, 2), datetime(2025, 10, 1), datetime(2025, 10, 2))
                
        temp_task_event = Event(temp_task, 20, 15, 10, 25)
        temp_task_event_2 = Event(temp_task_2, 20, 15, 10, 25)
        
        self.assertEqual(temp_task_event.get_startline(), None)
        self.assertEqual(temp_task_event_2.get_startline(), datetime(2025, 10, 1))
        
    def test_get_startline_invalid(self):
        task = Task("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1))
                
        task_event = Event(task, 20, 15, 10, 25)
        
        with self.assertRaises(ValueError):
            task_event.get_startline()

    def test_get_start_date(self):
        temp_task = TemporalTask("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1), datetime(2025, 10, 2))
                
        temp_task_event = Event(temp_task, 20, 15, 10, 25)
        
        self.assertEqual(temp_task_event.get_start_date(), datetime(2025, 10, 1))
        
    def test_get_start_date_invalid(self):
        task = Task("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1))
                
        task_event = Event(task, 20, 15, 10, 25)
        
        with self.assertRaises(ValueError):
            task_event.get_start_date()

    def test_get_end_date(self):
        temp_task = TemporalTask("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1), datetime(2025, 10, 2))
                
        temp_task_event = Event(temp_task, 20, 15, 10, 25)
        
        self.assertEqual(temp_task_event.get_end_date(), datetime(2025, 10, 2))
        
    def test_get_end_date_invalid(self):
        task = Task("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1))
                
        task_event = Event(task, 20, 15, 10, 25)
        
        with self.assertRaises(ValueError):
            task_event.get_end_date()

    def test_get_time_slot(self):
        temp_task = TemporalTask("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1), datetime(2025, 10, 2))
                
        temp_task_event = Event(temp_task, 20, 15, 10, 25)
        
        self.assertEqual(temp_task_event.get_time_slot(), TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))
        
    def test_get_time_slot_invalid(self):
        task = Task("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1))
                
        task_event = Event(task, 20, 15, 10, 25)
        
        with self.assertRaises(ValueError):
            task_event.get_time_slot()

class TimeTreeNodeTests(unittest.TestCase):
    def test_add_event(self):
        temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
        task_event = Event(temp_task, 20, 15, 10, 25)
        node = TimeTreeNode(task_event, TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))
        
        temp_task2 = TemporalTask("Make bed", "Remember after waking up to go to bed", datetime(2025, 10, 1), datetime(2025, 10, 2))
        temp_task3 = TemporalTask("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1), datetime(2025, 10, 2))

        task_event2 = Event(temp_task2, 10, 20, 10, 0)
        task_event3 = Event(temp_task3, 20, 15, 10, 25)
        
        node.add_event(task_event2)
        node.add_event(task_event3)
        
        self.assertIn(task_event2, node.events)
        self.assertIn(task_event3, node.events)
    
    def test_remove_event(self):
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
        
        self.assertIn(task_event2, node.events)
        self.assertIn(task_event3, node.events)

        node.remove_event("Make bed")
        
        self.assertNotIn(task_event2, node.events)
        self.assertIn(task_event3, node.events)
        
        node.remove_event(task_event3)
        
        self.assertNotIn(task_event2, node.events)
        self.assertNotIn(task_event3, node.events)

    def test_remove_event_invalid(self):
        temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
        task_event = Event(temp_task, 20, 15, 10, 25)
        node = TimeTreeNode(task_event, TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))
        
        with self.assertRaises(IndexError):
            node.remove_event(-1)
        with self.assertRaises(ValueError):
            node.remove_event("Anything")
        with self.assertRaises(TypeError):
            node.remove_event(datetime(2004, 10, 1))
        
        temp_task2 = TemporalTask("Make bed", "Remember after waking up to go to bed", datetime(2025, 10, 1), datetime(2025, 10, 2))
        temp_task3 = TemporalTask("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1), datetime(2025, 10, 2))

        task_event2 = Event(temp_task2, 10, 20, 10, 0)
        task_event3 = Event(temp_task3, 20, 15, 10, 25)
        
        node.add_event(task_event2)
        node.add_event(task_event3)
        node.remove_event(task_event)
        
        with self.assertRaises(IndexError):
            node.remove_event(-1)
        with self.assertRaises(IndexError):
            node.remove_event(1000)
        with self.assertRaises(ValueError):
            node.remove_event("Anything")
        with self.assertRaises(TypeError):
            node.remove_event(datetime(2004, 10, 1))
        with self.assertRaises(ValueError):
            node.remove_event(Event(temp_task, 20, 15, 10, 25))

    def test_get_num_events(self):
        temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
        task_event = Event(temp_task, 20, 15, 10, 25)
        node = TimeTreeNode(task_event, TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))
        
        self.assertEqual(1, node.get_num_events())
        
        temp_task2 = TemporalTask("Make bed", "Remember after waking up to go to bed", datetime(2025, 10, 1), datetime(2025, 10, 2))
        temp_task3 = TemporalTask("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1), datetime(2025, 10, 2))

        task_event2 = Event(temp_task2, 10, 20, 10, 0)
        task_event3 = Event(temp_task3, 20, 15, 10, 25)
        
        node.add_event(task_event2)
        node.add_event(task_event3)
        
        self.assertEqual(3, node.get_num_events())

    def test_get_event(self):
        temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
        task_event = Event(temp_task, 20, 15, 10, 25)
        node = TimeTreeNode(task_event, TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))
        
        self.assertEqual(task_event, node.get_event(0))
        self.assertEqual(task_event, node.get_event("Test"))

    def test_get_event_invalid(self):
        temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
        task_event = Event(temp_task, 20, 15, 10, 25)
        node = TimeTreeNode(task_event, TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))
        
        with self.assertRaises(IndexError):
            node.get_event(-1)
        with self.assertRaises(ValueError):
            node.get_event("Anything")
        with self.assertRaises(TypeError):
            node.get_event(datetime(2004, 10, 1))
        
        temp_task2 = TemporalTask("Make bed", "Remember after waking up to go to bed", datetime(2025, 10, 1), datetime(2025, 10, 2))
        temp_task3 = TemporalTask("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1), datetime(2025, 10, 2))

        task_event2 = Event(temp_task2, 10, 20, 10, 0)
        task_event3 = Event(temp_task3, 20, 15, 10, 25)
        
        node.add_event(task_event2)
        node.add_event(task_event3)
        node.remove_event(task_event)
        
        with self.assertRaises(IndexError):
            node.get_event(-1)
        with self.assertRaises(IndexError):
            node.get_event(1000)
        with self.assertRaises(ValueError):
            node.get_event("Anything")
        with self.assertRaises(TypeError):
            node.get_event(datetime(2004, 10, 1))

    def test_get_events(self):
        temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
        task_event = Event(temp_task, 20, 15, 10, 25)
        node = TimeTreeNode(task_event, TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))
        
        self.assertEqual([task_event], node.get_events())
        
        temp_task2 = TemporalTask("Make bed", "Remember after waking up to go to bed", datetime(2025, 10, 1), datetime(2025, 10, 2))
        temp_task3 = TemporalTask("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1), datetime(2025, 10, 2))

        task_event2 = Event(temp_task2, 10, 20, 10, 0)
        task_event3 = Event(temp_task3, 20, 15, 10, 25)
        
        node.add_event(task_event2)
        node.add_event(task_event3)
        
        events = node.get_events()
        
        self.assertIn(task_event, events)
        self.assertIn(task_event2, events)
        self.assertIn(task_event3, events)

    def test_get_key(self):
        temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
        task_event = Event(temp_task, 20, 15, 10, 25)
        node = TimeTreeNode(task_event, TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))
        
        self.assertEqual(TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)), node.get_key())

class TimeTreeTests(unittest.TestCase):
    def test_insertion(self):
        tree = TimeTree()
        
        temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
        task_event = Event(temp_task, 20, 15, 10, 25)
        tree.insert(task_event)

        self.assertEqual(task_event, tree.search(TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2))).get_event("Test"))

        temp_task2 = TemporalTask("Make bed", "Remember after waking up to go to bed", datetime(2025, 10, 3), datetime(2025, 10, 4))
        task_event2 = Event(temp_task2, 10, 20, 10, 25)
        tree.insert(task_event2)

        temp_task3 = TemporalTask("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1), datetime(2025, 10, 2))
        task_event3 = Event(temp_task3, 20, 15, 10, 25)
        tree.insert(task_event3)

        self.assertEqual(task_event3, tree.search(TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2))).get_event("Reminder"))
        self.assertEqual(2,  tree.search(TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2))).get_num_events())

        temp_task4 = TemporalTask("Another", "Example text", datetime(2025, 10, 5), datetime(2025, 10, 6))
        task_event4 = Event(temp_task4, 20, 15, 10, 25)
        tree.insert(task_event4)

        self.assertEqual(task_event4, tree.search(TimeInterval(datetime(2025, 10, 5), datetime(2025, 10, 6))).get_event("Another"))

    def test_insertion_multiple_schedule_intervals(self):
        tree = TimeTree()
        
        temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2), None, None, [TimeInterval(datetime(2025, 11, 1), datetime(2025, 11, 2)), TimeInterval(datetime(2025, 10, 5), datetime(2025, 10, 6))])
        task_event = Event(temp_task, 20, 15, 10, 25)
        tree.insert(task_event)

        self.assertEqual(task_event, tree.search(TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2))).get_event("Test"))
        self.assertEqual(task_event, tree.search(TimeInterval(datetime(2025, 11, 1), datetime(2025, 11, 2))).get_event("Test"))
        self.assertEqual(task_event, tree.search(TimeInterval(datetime(2025, 10, 5), datetime(2025, 10, 6))).get_event("Test"))
        self.assertEqual(3, tree.get_size())

    def test_get_size(self):
        tree = TimeTree()
        
        self.assertEqual(0, tree.get_size())
        
        temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
        task_event = Event(temp_task, 20, 15, 10, 25)
        tree.insert(task_event)

        self.assertEqual(1, tree.get_size())

        temp_task2 = TemporalTask("Make bed", "Remember after waking up to go to bed", datetime(2025, 10, 3), datetime(2025, 10, 4))
        task_event2 = Event(temp_task2, 10, 20, 10, 25)
        tree.insert(task_event2)

        self.assertEqual(2, tree.get_size())

        temp_task3 = TemporalTask("Reminder", "Remind Jasmine to water her plants", datetime(2025, 10, 1), datetime(2025, 10, 2))
        task_event3 = Event(temp_task3, 20, 15, 10, 25)
        tree.insert(task_event3)

        self.assertEqual(2, tree.get_size())

        tree.delete(task_event)

        self.assertEqual(2, tree.get_size())

        tree.delete(task_event3)

        self.assertEqual(1, tree.get_size())

    def test_delete(self):
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

        self.assertEqual(2,  tree.search(TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2))).get_num_events())

        tree.delete(task_event)

        self.assertEqual(1,  tree.search(TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2))).get_num_events())
        self.assertEqual(task_event3, tree.search(TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2))).get_event("Reminder"))

        tree.delete(task_event3)

        with self.assertRaises(ValueError):
            tree.search(TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)))

    def test_overlap_search(self):
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
        self.assertEqual(3, len(search_events))
        for event in search_events:
            assert(event['event'] in events) 

    def test_search(self):
        tree = TimeTree()
        
        temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
        task_event = Event(temp_task, 20, 15, 10, 25)
        tree.insert(task_event)

        self.assertEqual(task_event, tree.search(TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2))).get_event("Test"))

    def test_search_invalid(self):
        tree = TimeTree()
        
        temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
        task_event = Event(temp_task, 20, 15, 10, 25)
        tree.insert(task_event)

        with self.assertRaises(ValueError):
            tree.search(TimeInterval(datetime(2025, 10, 2), datetime(2025, 10, 3)))

    def test_sweepline_overlap_search(self):
        # TODO: Test this overlap search function
        pass

class CalendarTests(unittest.TestCase):
    # def test_time_interval_constraint(self):
        # test_csp = CSP()

        # temp_interval1 = TimeInterval(datetime(2025, 10, 1, 6, 30), datetime(2025, 10, 1, 7))
        # temp_interval2 = TimeInterval(datetime(2025, 10, 1, 7, 30), datetime(2025, 10, 1, 8, 30))
        # self.assertFalse(test_csp._time_interval_constraint(temp_interval1, temp_interval2, temp_interval1.get_duration(), temp_interval2.get_duration()))

    def test(self):
        cal = Calendar()

        temp_task = TemporalTask("B", "B", datetime(2025, 10, 2, 6, 30), datetime(2025, 10, 2, 7), None, None, [TimeInterval(datetime(2025, 10, 2, 8), datetime(2025, 10, 2, 8, 30))])
        cal.schedule_event(temp_task, 20, 15, 10, 25)

        temp_task2 = TemporalTask("A", "A", datetime(2025, 10, 2, 7), datetime(2025, 10, 2, 7, 30), None, None, [TimeInterval(datetime(2025, 10, 2, 6), datetime(2025, 10, 2, 7)), TimeInterval(datetime(2025, 10, 2, 7, 30), datetime(2025, 10, 2, 8))])
        cal.schedule_event(temp_task2, 20, 15, 10, 25)

        temp_task3 = TemporalTask("C", "C", datetime(2025, 10, 2, 7, 30), datetime(2025, 10, 2, 8, 30))
        cal.schedule_event(temp_task3, 20, 15, 10, 25)

        cal.generate_schedule(datetime(2025, 10, 2))

    # def test_add_event(self):
    #     calendar = Calendar()
        
    # temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
    # calendar.schedule_event(temp_task, 20, 15, 10, 25)

    #     self.assertEqual(temp_task, calendar.get_events(TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)), "Test")[0].get_task("Test"))

    # def test_remove_event(self):
    #     calendar = Calendar()
        
    #     temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
    #     task_event = Event(temp_task, 20, 15, 10, 25)
    #     calendar.add_event(task_event)

    #     calendar.remove_event(TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)), "Test")

    #     with self.assertRaises(ValueError):
    #         calendar.get_event(TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)), "Test")

    # def test_remove_event_invalid(self):
    #     calendar = Calendar()
        
    #     temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
    #     task_event = Event(temp_task, 20, 15, 10, 25)
    #     calendar.add_event(task_event)

    #     with self.assertRaises(ValueError):
    #         calendar.remove_event(TimeInterval(datetime(2025, 10, 2), datetime(2025, 10, 3)), "Test")
    #     with self.assertRaises(ValueError):
    #         calendar.remove_event(TimeInterval(datetime(2025, 10, 1), datetime(2025, 10, 2)), "Anything")

    # def test_get_event(self):
    #     calendar = Calendar()
        
    #     temp_task = TemporalTask("Test", "Example text", datetime(2025, 10, 1), datetime(2025, 10, 2))
    #     task_event = Event(temp_task, 20, 15, 10, 25)
    #     calendar.add_event(task_event)

    #     self.assertEqual(task_event, calendar

if __name__ == '__main__':
    unittest.main()