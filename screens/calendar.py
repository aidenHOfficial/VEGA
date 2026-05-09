import calendar
from datetime import date, datetime, timedelta

from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from typing import TYPE_CHECKING

from controllers.main_controller import Controller

if TYPE_CHECKING:
    from app import MyApp

class DaySchedule(Horizontal):

    def __init__(self, controller: Controller):
        super().__init__()
        self.controller = controller

    def compose(self):
        yield Vertical(id="events")

    def on_mount(self):
        d = date.today() 

        day_start = datetime(d.year, d.month, d.day, 0, 0, 0)
        day_end = datetime(d.year, d.month, d.day, 23, 59, 59)

        events = self.controller.get_events(
            start_date=day_start, 
            end_date=day_end
        )

        container = self.query_one("#events")

        if events is None:
            container.mount(Static("No events!"))
            return

        for event in events:
            container.mount(Static(str(event)))

class WeekSchedule(Horizontal):

    def __init__(self, controller: Controller):
        super().__init__()
        self.controller = controller

    def compose(self):
        yield Vertical(id="events")

    def on_mount(self):
        d = date.today() 
        day_index = d.weekday()

        week_start = d - timedelta(days=day_index)
        week_end = d + timedelta(days=(6 - day_index))

        events = self.controller.get_events(
            start_date=week_start, 
            end_date=week_end
        )

        container = self.query_one("#events")

        if events is None:
            container.mount(Static("No events!"))
            return

        for event in events:
            container.mount(Static(str(event)))

class MonthSchedule(Horizontal):

    def __init__(self, controller: Controller):
        super().__init__()
        self.controller = controller

    def compose(self):
        yield Vertical(id="events")

    def on_mount(self):
        d = date.today()

        month_start = datetime(d.year, d.month, 1)
        days_in_month = calendar.monthrange(d.year, d.month)[1]
        month_end = datetime(d.year, d.month, days_in_month, 23, 59, 59)

        events = self.controller.get_events(
            start_date=month_start,
            end_date=month_end
        )

        container = self.query_one("#events")

        if events is None:
            container.mount(Static("No events!"))
            return

        for event in events:
            container.mount(Static(str(event)))

class CalendarScreen(Screen):
    @property
    def app(self) -> "MyApp":
        return super().app

    @property
    def controller(self):
        return self.app.controller

    def compose(self) -> ComposeResult:

        yield DaySchedule(self.controller)
        yield WeekSchedule(self.controller)
        yield MonthSchedule(self.controller)