import curses
import datetime
import math
from enum import Enum

ascii_title = """
 _    _________________ 
| |  / / ____/ ____/   |
| | / / __/ / / __/ /| |
| |/ / /___/ /_/ / ___ |
|___/_____/\____/_/  |_|"""
subtitle = "Scheduler and Personalized Assistant"

goals = []
callendar_events = [{datetime.date(2025, 6, 22): {"events": [{"title": "Wake up", "time": datetime.datetime(2025, 6, 22, 7, 30, 0), "description": "Wake up early for the busy day"}]}}]

DA = 1 # Deadline aggression
RC = 1 # Rescheduling cost

GW = 1 # Goal weight
RW = 1 # Routine weight
PW = 1 # Personal weight
RW = 1 # Relational weight

class Task:
    def __init__(self, title: str, description: str):
        self.title = title
        self.description = description
        self.completed = False

    def __str__(self):
        print(f"Title: {self.title} Description: {self.description} Completed: {self.completed}")

class TemporalTask:
    def __init__(self, title: str, description: str, start_date: datetime.datetime, end_date: datetime.datetime, repeated_time_difference: datetime.timedelta):
        super().__init__(title, description)

        self.start_date = start_date
        self.end_date = end_date
        self.repeated_time_difference = repeated_time_difference

    def __str__(self):
        return f"Title: {self.title} Description: {self.description} Complete Date: {self.complete_date}, Completed: {self.completed}"

    def get_total_time(self):
        if (self.start_date is not None and self.end_date is not None):
            return self.end_date - self.start_date
        return None
    
    def get_time_slot(self):
        if (self.start_date is not None and self.end_date is not None):
            return self.start_date, self.end_date
        return None
    
    def get_next_time_slot(self, multiple: int):
        if (multiple < 1):
            raise ValueError("Multiple not greater than 1")
        if (self.start_date is not None and self.end_date is not None):
            return (self.start_date + self.repeated_time_difference * multiple), (self.end_date + self.repeated_time_difference)
        return None

class Goal(Task):    

    def __init__(self, title: str, description: str, start_date: datetime.datetime, end_date: datetime.datetime, repeated_time_difference: datetime.timedelta):
        super().__init__(title, description)

        self.start_date = start_date
        self.end_date = end_date
        self.subgoals = []
        self.completed_steps = 0
    
    def __str__(self):
        return f"Title: {self.title} Description: {self.description} Start Date: {self.start_date} Complete Date: {self.complete_date} Completed: {self.completed} Subgoals: {self.subgoals} "
    
    def check_index(self, index):
        if index is None or index < 0 or index >= len(self.subgoals):
            raise IndexError("Invalid subgoal index")
        
    def check_completion(self):
        completed_steps = 0

        for subgoal in self.subgoals:
            if (subgoal.completed == True):
                completed_steps += 1

        self.completed_steps = completed_steps

        if (self.completed_steps == len(self.subgoals) - 1):
            self.completed = True
        else:
            self.completed = False
        
        return completed_steps

    def get_num_subgoals(self):
        return len(self.subgoals)
    
    def get_subgoal(self, index: int):
        self.check_index(index)

        return self.subgoals[index]
    
    def get_next_subgoal(self):
        for subgoal in self.subgoals:
            if (subgoal.complete == False):
                return subgoal
        return None

    def get_subgoal_list(self):
        return self.subgoals

    def add_subgoal(self, title: str, description: str, start_date: datetime.datetime, end_date: datetime.datetime):
        self.subgoals.append(TemporalTask(title, description, start_date, end_date, None))
        
        self.subgoals.sort(key=lambda x: x.start_date)

        self.check_completion()

    def remove_subgoal(self, index: int):
        self.check_index(index)

        del self.subgoals[index]

        self.check_completion()
        
    def complete_subgoal(self, index: int):
        self.check_index(index)

        self.subgoals[index].completed = True

        self.check_completion()

    def get_progress_fraction(self):
        self.check_completion()

        return f"{self.completed_steps}/{len(self.subgoals)}"
    
    def get_progress_percent(self):
        self.check_completion()

        if not self.subgoals:
            return 100.0  # Avoid division by zero; if no subgoals, consider complete
        return (self.completed_steps / len(self.subgoals)) * 100
    
class Routine(Task):

    def __init__(self, title, description, start_time, time_between: datetime.timedelta):
        super().__init__(title, description)

        self.start_time = start_time
        self.time_between = time_between
        self.total_estimated_time = datetime.timedelta(0, 0, 0, 0, 0, 0, 0)

        self.items = []

    def check_index(self, index):
        if index is None or index < 0 or index >= len(self.subgoals):
            raise IndexError("Invalid subgoal index")

    def get_routine_tasks(self):
        return self.items
    
    def get_routine_task(self, index):
        self.check_index(index)

        return self.items[index]
    
    def get_time_slot(self):
        return self.start_time, self.total_estimated_time + self.start_time
    
    def get_total_time(self):
        return self.total_estimated_time

    def add_routine_task(self, task, complete_time: datetime.timedelta):
        if (task not in self.items):
            self.items.add(task)
            self.total_estimated_time += complete_time


def output_to_file(string):
    with open("debug.txt", "a") as f:
        f.write(string + "\n")


def get_urgency_score(event):
    # Returns a score between 0 and 10

    time_diffrerence = None
    shift = 0.202732554054
    m = 5

    if ("deadline" in event):
        time_diffrerence = (event["deadline"] - datetime.now()).hours()
        shift = 0.69314718056
    else:
        time_diffrerence = (event["time"] - datetime.now()).hours()

    # m * tanh(t+s) + m
    return m * ((math.e**(time_diffrerence + shift) - math.e**(-(time_diffrerence + shift))) / (math.e**(time_diffrerence + shift) + math.e**(-(time_diffrerence + shift)))) + m

def get_priority_score(event):
    return max((GW * event["goal_value"]) + (RW * event["routine_value"]) + (PW * event["personal_value"]) + (RW * event["relational_value"]), 10)

def schedule_new_event(task: Task, goal_importance: float, routine_importance: float, personal_importance: float):
    date = datetime.date()
    if (date < datetime.now()):
        return False

    if (date not in callendar_events):
        callendar_events[date] = {"events": []}
    
    callendar_events[date]["events"].append({"task": task, "goal_importance": goal_importance, "routine_importance": routine_importance, "personal_importance": personal_importance})





def print_menu_items(menu_pad, menu_options, selected_option_index, width, menu_row_sections):
    for i, option in enumerate(menu_options):
        x = width // 2 - len(option) // 2
        y = menu_row_sections[0] + i
        if i == selected_option_index:
            menu_pad.attron(curses.color_pair(3))
            menu_pad.addstr(y, x, option)
            menu_pad.attroff(curses.color_pair(3))
        else:
            menu_pad.addstr(y, x, option)

def print_menu_titles(menu_pad, width, title_rows, subtitle_rows):
    # Print title in green
    menu_pad.attron(curses.color_pair(1))
    for idx, line in enumerate(ascii_title.strip("\n").splitlines()):
        menu_pad.addstr(title_rows[0] + idx, width // 2 - len(line) // 2, line)
    menu_pad.attroff(curses.color_pair(1))

    # Print subtitle in white
    menu_pad.attron(curses.color_pair(2))
    menu_pad.addstr(subtitle_rows[0], width // 2 - len(subtitle) // 2, subtitle)
    menu_pad.attroff(curses.color_pair(2))

def print_menu_window(stdscr, menu_options, selected_option_index, menu_row_sections, x_padding, y_padding):
    height, width = stdscr.getmaxyx()
    menu_height, menu_width = int(menu_row_sections["height"]), (width - (x_padding * 2))

    menu_pad = curses.newpad(menu_height, menu_width)
    menu_pad.border()
    menu_pad.addstr(0, 2, " MENU ")

    # Use the menu_pad for all content
    print_menu_titles(menu_pad, (menu_width - (x_padding * 2)), menu_row_sections["title"], menu_row_sections["subtitle"])
    print_menu_items(menu_pad, menu_options, selected_option_index, (menu_width - (x_padding * 2)), menu_row_sections["menu_options"])

    menu_pad.refresh(0, 0, 0, 0, height-1, width-1)

def run_menu_window(stdscr, menu_options, row_sections, x_padding, y_padding):
    selected_option_index = 0
    menu_row_sections = row_sections["menu"]

    print_menu_window(stdscr, menu_options, selected_option_index, menu_row_sections, x_padding, y_padding)

    while True:
        key = stdscr.getch()

        if (key != -1):
            output_to_file(f"key: {key}")

        if key in [ord('w'), ord('W'), 450]:  # Up
            selected_option_index = (selected_option_index - 1) % len(menu_options)

        elif key in [ord('s'), ord('S'), 456]:  # Down
            selected_option_index = (selected_option_index + 1) % len(menu_options)

        elif key in [curses.KEY_ENTER, 10, 13]:  # Enter
            selected_option = menu_options[selected_option_index]
            if selected_option == "View Schedule":
                run_schedule_window(stdscr, row_sections, x_padding, y_padding)
            elif selected_option == "Preferences":
                run_preferences_window()
            elif selected_option == "Chat":
                run_chat_window()
            return menu_options[selected_option_index]

        print_menu_window(stdscr, menu_options, selected_option_index, menu_row_sections, x_padding, y_padding)




def run_schedule_window(stdscr, row_sections, x_padding, y_padding):
    schedule_row_sections = row_sections["schedule"]

    print_schedule_window(stdscr, schedule_row_sections, x_padding, y_padding)

def print_day_title(title_win, day_events):
    height, width = title_win.getmaxyx()

    date = day_events["date"]

    title_win.attron(curses.color_pair(2))
    title_win.addstr(0, (width // 2 - (len(date) // 2)), date)
    title_win.addstr(1, 0, "_" * width)
    title_win.attroff(curses.color_pair(2))

def print_schedule_hours(hours_win, width, day_events):
    timespan = timespan(min(datetime.datetime(2025, 6, 22, 6, 0, 0), day_events[0]["time"]), datetime.datetime(2025, 6, 22, 11, 59, 0))

    

    # hours_win.addstr(subtitle_rows[0], width // 2 - len(subtitle) // 2, subtitle)

def print_schedule_todos(todo_win, width, day_events):
    print("")

def print_schedule_window(stdscr, x_padding, y_padding, day_events):
    height, width = stdscr.getmaxyx()
    stdscr.clear()
    
    schedule_pad = curses.newwin(height - y_padding, width - x_padding, y_padding, x_padding)
    schedule_pad.border()
    schedule_pad.addstr(0, 2, " SCHEDULE ")

    hours_win_width = (width * 2) / 3
    todo_win_width = width / 3

    # example day_events data structure where: 
    #   date is the selected view date,
    #   events is the list of events in chronological order
    day_events = 

    title_win = schedule_pad.derwin(2, hours_win_width, 1, 1)
    hours_win = schedule_pad.derwin(height-4, hours_win_width, 3, 1)
    todo_win = schedule_pad.derwin(height-4, todo_win_width, 3, todo_win_width + 1)
    
    print_day_title(title_win, day_events)
    print_schedule_hours(hours_win, (hours_win_width - (x_padding * 2)), day_events)
    print_schedule_todos(todo_win, todo_win_width, day_events)

    schedule_pad.refresh(0, 0, 0, 0, height-1, width-1)



def run_preferences_window(stdscr, row_sections, x_padding, y_padding):
    preferences_row_sections = row_sections["preferences"]

    print_preferences_window(stdscr, x_padding, y_padding, preferences_row_sections)

def print_preferences_window(stdscr, preferences_row_sections, x_padding, y_padding):
    height, width = stdscr.getmaxyx()
    stdscr.clear()

    menu_win = curses.newwin(height - y_padding, width - x_padding, y_padding, x_padding)
    menu_win.border()
    menu_win.addstr(0, 2, " PREFERENCES ")

    stdscr.refresh()



def run_chat_window(stdscr, row_sections, x_padding, y_padding):
    chat_row_sections = row_sections["chat"]
    
    print_chat_window(stdscr, x_padding, y_padding, chat_row_sections)

def print_chat_window(stdscr, chat_row_sections, x_padding, y_padding):
    height, width = stdscr.getmaxyx()
    stdscr.clear()

    menu_win = curses.newwin(height - y_padding, width - x_padding, y_padding, x_padding)
    menu_win.border()
    menu_win.addstr(0, 2, " CHAT ")

    stdscr.refresh()



def main(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)
    stdscr.nodelay(True)
    stdscr.clear()
    curses.start_color()
    
    # Title color scheme
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    # Normal text color scheme
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    # Highlighted text color scheme
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    x_padding = 2
    y_padding = 3
    height, width = stdscr.getmaxyx()
    output_to_file(f"starting width: {width}, height: {height}")
    menu_options = ['View Schedule', 'Preferences', 'Chat', 'Exit']
    row_sections = {
        "menu": {
            "height": (y_padding * 2) + 10 + len(menu_options),
            "title": (y_padding, y_padding + 5),
            "subtitle": (y_padding + 6, y_padding + 8),
            "menu_options": (y_padding + 10, y_padding + 10 + len(menu_options)),
        },
        "schedule": {
            "daily_view": (x_padding, 12),
            "weekly_view": (13, 23),
            "monthly_view": (24, 34)
        }
    }

    run_menu_window(stdscr, menu_options, row_sections, x_padding, y_padding)

    stdscr.getch()


if __name__ == "__main__":
    curses.wrapper(main)