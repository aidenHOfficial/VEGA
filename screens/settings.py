from textual.widgets import Static
from textual.containers import Vertical
from textual.screen import Screen

class SettingsScreen(Screen):
    def compose(self):
        yield Static("Settings page")