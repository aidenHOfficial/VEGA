import unittest
from models import Task, TemporalTask, Goal
from datetime import datetime

print("\n\n")

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
    
    def test__str__(self):
        deadline_task = Task("test", "this is a test task", datetime(2004,1,1))
        self.assertEqual(deadline_task.__str__(), f"Task(_title='test', _description='this is a test task', _completed=False, _deadline=datetime.datetime(2004, 1, 1, 0, 0))")

        no_deadline_task = Task("test2", "this is a second test task")
        self.assertEqual(no_deadline_task.__str__(), f"Task(_title='test2', _description='this is a second test task', _completed=False, _deadline=None)")

        completed_task = Task("test3", "this is a third test task")
        completed_task._completed = True
        self.assertEqual(completed_task.__str__(), f"Task(_title='test3', _description='this is a third test task', _completed=True, _deadline=None)")

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
        
    def test_constructor_with_invalid_reschedules(self):
        reschedules = [(1, 2), (3, 4)]
        with self.assertRaises(ValueError):
            TemporalTask("test", "this is a test task", datetime(2025, 10, 1), datetime(2025, 10, 31), reschedule_periods=reschedules)
    
        reschedules = [(datetime(2025, 10, 1), datetime(2025, 10, 2)), (datetime(2025, 10, 3), datetime(2025, 10, 4))]
        with self.assertRaises(ValueError):
            TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10), deadline=datetime(2025, 10, 9), reschedule_periods=reschedules)
        
        with self.assertRaises(ValueError):
            TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10), startline=datetime(2025, 10, 2), reschedule_periods=reschedules)

    def test__str__(self):
        task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10), reschedule_periods=[(datetime(2025, 10, 3), datetime(2025, 10, 11))])
        self.assertEqual(task.__str__(), "TemporalTask(_title='test', _description='this is a test task', _completed=False, _deadline=None, _start_date=datetime.datetime(2025, 10, 2, 0, 0), _end_date=datetime.datetime(2025, 10, 10, 0, 0), _startline=None, _reschedule_periods=[(datetime.datetime(2025, 10, 3, 0, 0), datetime.datetime(2025, 10, 11, 0, 0))])")

    def test_get_start_date(self):
        task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10))
        self.assertEqual(task.get_start_date(), datetime(2025, 10, 2))

    def test_get_end_date(self):
        task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10))
        self.assertEqual(task.get_end_date(), datetime(2025, 10, 10))
    
    def test_get_start_line(self):
        task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10), datetime(2025, 10, 2))
        self.assertEqual(task.get_start_line(), datetime(2025, 10, 2))

    def test_get_total_time(self):
        task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10))
        self.assertEqual(task.get_total_time(), datetime(2025, 10, 10) - datetime(2025, 10, 2))

    def test_get_time_slot(self):
        task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10))
        self.assertEqual(task.get_time_slot(), (datetime(2025, 10, 2), datetime(2025, 10, 10)))

    def test_get_reschedule_period_no_values(self):
        task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10))
        self.assertEqual(task.get_reschedule_periods(), [])

    def test_get_reschedule_period_with_values(self):
        task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10), reschedule_periods=[(datetime(2025, 10, 3), datetime(2025, 10, 11))])
        self.assertEqual(task.get_reschedule_periods(), [(datetime(2025, 10, 3), datetime(2025, 10, 11))])

    def test_add_reschedule_period(self):
        task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10))
        task.add_reschedule_period((datetime(2025, 10, 3), datetime(2025, 10, 11)))
        self.assertEqual(task.get_reschedule_periods(), [(datetime(2025, 10, 3), datetime(2025, 10, 11))])
        
        task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10), datetime(2025, 10, 2), datetime(2025, 10, 10))
        task.add_reschedule_period((datetime(2025, 10, 2), datetime(2025, 10, 10)))
        self.assertEqual(task.get_reschedule_periods(), [(datetime(2025, 10, 2), datetime(2025, 10, 10))])
        
    def test_add_reschedule_period_invalid_values(self):
        task = TemporalTask("test", "this is a test task", datetime(2025, 10, 2), datetime(2025, 10, 10), datetime(2025, 10, 2), datetime(2025, 10, 10))
        with self.assertRaises(ValueError):
            self.assertRaises(ValueError, task.add_reschedule_period((datetime(2025, 10, 1), datetime(2025, 10, 10))))
        with self.assertRaises(ValueError):
            self.assertRaises(ValueError, task.add_reschedule_period((datetime(2025, 10, 2), datetime(2025, 10, 12))))

class GoalTests(unittest.TestCase):
    def getDummyGoal(self):
        goal = Goal("Root Goal", "Example text", datetime(2025, 10, 1), datetime(2026, 10, 1), datetime(2025, 10, 1), datetime(2026, 10, 1))
        
        sub_goal_A = Goal("Subgoal A", "Example text", datetime(2025, 10, 1), datetime(2026, 3, 30), datetime(2025, 10, 1), datetime(2026, 3, 30))
        sub_goal_AA = Goal("Subgoal AA", "Example text", datetime(2025, 10, 1), datetime(2025, 12, 30), datetime(2025, 10, 1), datetime(2025, 12, 30))
        
        sub_goal_B = Goal("Subgoal B", "Example text", datetime(2026, 3, 30), datetime(2026, 10, 1), datetime(2026, 3, 30), datetime(2026, 10, 1))
        sub_goal_BA = Goal("Subgoal BA", "Example text", datetime(2026, 3, 30), datetime(2026, 5, 1), datetime(2026, 3, 30), datetime(2026, 5, 1))
        sub_goal_BB = Goal("Subgoal BB", "Example text", datetime(2026, 5, 1), datetime(2026, 10, 1), datetime(2026, 5, 1), datetime(2026, 10, 1))
        
        sub_goal_A.add_subgoal(sub_goal_AA)
        
        sub_goal_B.add_subgoal(sub_goal_BA)
        sub_goal_B.add_subgoal(sub_goal_BB)
        
        goal.add_subgoal(sub_goal_A)
        goal.add_subgoal(sub_goal_B)
        
        return goal
    
    def test_add_subgoal(self):
        goal = self.getDummyGoal()
        
        sub_goal_A = goal.get_subgoal(0)
        sub_goal_AB = Goal("Subgoal AB", "this is a dummy goal", datetime(2025, 10, 1), datetime(2026, 3, 30))
        sub_goal_A.add_subgoal(sub_goal_AB)
        
        self.assertEqual(sub_goal_AB, goal.get_subgoal(0).get_subgoal(1))
        
    def test_complete_subgoal(self):
        goal = self.getDummyGoal()
        
        goal.complete_subgoal(0)
        
        self.assertEqual(goal.get_completion_status(), 2)
        
    def test_get_completion_status(self):
        goal = Goal("Root Goal", "Example text", datetime(2025, 10, 1), datetime(2026, 10, 1), datetime(2025, 10, 1), datetime(2026, 10, 1))
        
        self.assertEqual(goal.get_completion_status(), 0)
        
        sub_goal_A = Goal("Subgoal A", "Example text", datetime(2025, 10, 1), datetime(2026, 3, 30), datetime(2025, 10, 1), datetime(2026, 3, 30))

        goal.add_subgoal(sub_goal_A)
        
        self.assertEqual(goal.get_completion_status(), 0)
        
        goal.complete_subgoal(0)
        
        self.assertEqual(goal.get_completion_status(), 1)


if __name__ == '__main__':
    unittest.main()