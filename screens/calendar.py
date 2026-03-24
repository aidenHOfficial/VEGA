from textual.app import ComposeResult, RenderResult
from textual.widgets import Header, ListItem, ListView, Label, Static
from rich.text import Text
from textual.containers import Horizontal
from textual.screen import Screen
from textual import log

class DaySchedule(Horizontal):

    def compose(self):
        yield Static("todo")

class WeekSchedule(Horizontal):

    def compose(self):
        yield Static("todo")

class MonthSchedule(Horizontal):

    def compose(self):
        yield Static("todo")

class CalendarScreen(Screen):
    def compose(self) -> ComposeResult:
        yield DaySchedule()
        yield WeekSchedule()
        yield MonthSchedule()