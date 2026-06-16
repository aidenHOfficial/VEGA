from models.scheduled_event import ScheduledEvent
from models.task import Task
from models.time_interval import TimeInterval
from repositories.calendar_repository import CalendarRepository

class Controller():
    DEFAULT_GOAL_VALUE = 20
    DEFAULT_ROUTINE_VALUE = 20
    DEFAULT_PERSONAL_VALUE = 20
    DEFAULT_RELATIONAL_VALUE = 20

    def __init__(self, repository: CalendarRepository):
        self.repository = repository
        self.calendar = repository.load_calendar()

    def schedule_task(self, task: Task):
        self.calendar.schedule_event(
            task=task,
            goal_value=self.DEFAULT_GOAL_VALUE,
            routine_value=self.DEFAULT_ROUTINE_VALUE,
            personal_value=self.DEFAULT_PERSONAL_VALUE,
            relational_value=self.DEFAULT_RELATIONAL_VALUE
        )
        self.repository.save_calendar(self.calendar)
    
    def get_events(self, interval: TimeInterval) -> list[ScheduledEvent]:
        return self.calendar.get_events(interval=interval)