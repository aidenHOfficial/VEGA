from textual.app import ComposeResult, RenderResult
from textual.widgets import Header, ListItem, ListView, Label, Static
from rich.text import Text
from textual.containers import Vertical
from textual.screen import Screen
from textual import log

subtitle = "Scheduler and Personalized Assistant"

class MenuItem(ListItem):
    def __init__(self, item_text: str, **kwargs):
        self.item_text = item_text
        super().__init__(**kwargs)

    def compose(self):
        yield Label(self.item_text, classes="centered-item bordered halfwidth")

class Menu(Vertical):
    BINDINGS = [("enter", "select", "Select")]
    button_options = ["Calendar", "Chats", "Settings"]

    def compose(self):
        yield ListView(
            *[MenuItem(option, id=option.lower(), classes="centered-item") for option in self.button_options]
        )

    def on_list_view_selected(self):
        list_view = self.query_one(ListView)
        item = list_view.highlighted_child

        if item:
            selected = item.id
            if selected in self.app.SCREENS:
                self.app.switch_screen(selected)
            else:
                self.app.log(f"Unknown screen: {selected}")

class AsciiTitle(Static):
    def __init__(self):
        super().__init__()

    def on_mount(self):
        with open("logo/logo.txt", "r", encoding="utf-8") as f:
            ascii_lines = f.readlines()

        with open("logo/logo_mask.txt", "r", encoding="utf-8") as f:
            mask_lines = f.readlines()

        styled = Text()
        for line, mask in zip(ascii_lines, mask_lines):
            for ch, m in zip(line.rstrip("\n"), mask.rstrip("\n")):
                if m == "1":
                    styled.append(ch, style="bold black on green")
                else:
                    styled.append(ch)

            styled.append("\n")

        self.update(styled)

class HomeScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield AsciiTitle()
        yield Menu()