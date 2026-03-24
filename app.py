from textual.app import App
from screens.home import HomeScreen
from screens.settings import SettingsScreen
from screens.calendar import CalendarScreen

class MyApp(App):
    SCREENS = {
        "home": HomeScreen,
        "settings": SettingsScreen,
        "calendar": CalendarScreen
    }
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("h", "go_home", "Home")
    ]
    CSS_PATH = "styles.tcss"

    def action_go_home(self):
        self.switch_screen("home")

    def on_mount(self):
        self.push_screen("home")

if __name__ == "__main__":
    app = MyApp()
    app.run()