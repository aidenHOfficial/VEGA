import calendar
from collections import defaultdict
from datetime import date, datetime, timedelta
from enum import Enum

from rich import box
from rich.console import Group
from rich.table import Table
from rich.text import Text
from textual.app import ComposeResult
from textual.widgets import Button, Header, Static
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from rich.table import Table
from typing import TYPE_CHECKING, Iterable

from controllers.main_controller import Controller
from models.scheduled_event import ScheduledEvent
from models.time_interval import TimeInterval

if TYPE_CHECKING:
    from app import MyApp

TOP_FILL = "‾"

def _get_day_interval(d: date):
    day_start = datetime(d.year, d.month, d.day, 0, 0, 0)
    day_end = datetime(d.year, d.month, d.day, 23, 59, 59)

    return TimeInterval(day_start, day_end)

def _get_week_interval(d: date):
    day_index = d.weekday()

    week_start = d - timedelta(days=day_index)
    week_end = d + timedelta(days=(6 - day_index))

    return TimeInterval(week_start, week_end)

def _get_month_interval(d: date):
    month_start = datetime(d.year, d.month, 1)
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    month_end = datetime(d.year, d.month, days_in_month, 23, 59, 59)

    return TimeInterval(month_start, month_end)

class DaySchedule(Horizontal):

    events_by_hour: dict = defaultdict(list)

    def __init__(self, controller: Controller, selected_day: date):
        super().__init__()
        self.controller = controller
        self.selected_day = selected_day

    def compose(self):
        yield Vertical(id="events")

    def on_mount(self):
        scheduled_events = self.controller.get_events(_get_day_interval(self.selected_day))
        
        for sched in scheduled_events():
            self.events_by_hour[sched.interval.get_start_date().strftime("%I:%M %p")].append(sched)

    def render(self):
        table = Table.grid(expand=True)

        table.add_column(width=12)
        table.add_column(ratio=1)

        for hour in range(24):
            label = datetime.time(hour).strftime("%I:00 %p")
            hour_events = self.events_by_hour[label]
            table.add_row(
                label,
                "[green][/green]"
            )

        return table
    
class DayScheduleTable:
    def __init__(self, day: date, events: Iterable[ScheduledEvent] | None, interval: int = 15):
        self.day = day
        self.events = events 
        self.selection = 0
        self.interval = interval

    def render(self) -> Group:
        table = Table(
            title=f"{self.day:%A, %B} {self.day.day}, {self.day.year}",
            box=box.ROUNDED,
            expand=True,
            show_lines=False,
            pad_edge=False,
        )

        table.add_column("Time", style="bold", no_wrap=True, width=10)

        class PointStatus(Enum):
            STARTING = 0
            CURRENT = 1
            ENDING = 2

        points = []
        for e in self.events:
            time = e.interval
            event = e.event
            points.append((time, time.start_date, 1, event))
            points.append((time, time.end_date, -1, event))
        points.sort(key=lambda x: (x[1], -x[2]))
    
        total_minutes = 1440
        lanes = [] 

        for m in range(0, total_minutes + 1, self.interval):
            if m in points:
                for task, event_type in points[m]:
                    if event_type == PointStatus.STARTING:

                        assigned_lane = -1
                        for idx, lane_task in enumerate(lanes):
                            if lane_task is None:
                                lanes[idx] = task
                                assigned_lane = idx
                                break

                        if assigned_lane == -1:
                            lanes.append(task)
                            assigned_lane = len(lanes) - 1
                            table.add_column(f"Lane {assigned_lane + 1}")

                        task.event_type = PointStatus.STARTING

                    elif event_type == PointStatus.ENDING:
                        if task in lanes:
                            idx = lanes.index(task)
                            lanes[idx] = None
                            task.event_type = PointStatus.ENDING

            row_cells = []
            for idx, task in enumerate(lanes):
        
                if task is None:
                    row_cells[idx] = ""
                else:
                    status = getattr(task, 'event_type', PointStatus.STARTING)
                    if status == PointStatus.STARTING:
                        row_cells[idx] = f"[{task.title}]"
                        task.event_type = PointStatus.CURRENT
                    elif status == PointStatus.ENDING:
                        row_cells[idx] = "________"
                    else:
                        row_cells[idx] = "|"

            hour = (m // 60) % 12
            hour = 12 if hour == 0 else hour
            minute = f"{m % 60:02d}"
            ampm = "AM" if m < 720 or m == 1440 else "PM"
            label = f"{hour}:{minute} {ampm}"
    
            table.add_row(label, **row_cells)

        legend = Text(
            "Up/down moves time. Left/right moves lanes. Shift+up/down selects a time range across lanes.",
            style="dim",
        )
        return Group(table, legend)

class CalendarScreen(Screen):
    @property
    def app(self) -> "MyApp":
        return super().app

    @property
    def controller(self):
        return self.app.controller
    
    def __init__(self):
        super().__init__()
        self.selected_day = date.today()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="calendar-layout"):
            yield DaySchedule()
            # yield CalendarTaskForm(id="calendar-form")