import curses

ascii_title = """
 _    _________________ 
| |  / / ____/ ____/   |
| | / / __/ / / __/ /| |
| |/ / /___/ /_/ / ___ |
|___/_____/\____/_/  |_|"""
subtitle = "Scheduler and Personalized Assistant"



def output_to_file(string):
    with open("debug.txt", "a") as f:
        f.write(string + "\n")



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

    output_to_file(f"menu_width: {menu_width}, menu_height: {menu_height}")
    output_to_file(f"main_width: {width}, main_height: {height}")
    output_to_file(f"main_dim - menu_dim: width: {width - menu_width}, height: {height - menu_height}")

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

    print_schedule_window(stdscr, x_padding, y_padding, schedule_row_sections)

def print_schedule_window(stdscr, schedule_row_sections, x_padding, y_padding):
    height, width = stdscr.getmaxyx()
    stdscr.clear()

    schedule_win = curses.newwin(height - y_padding, width - x_padding, y_padding, x_padding)
    schedule_win.border()
    schedule_win.addstr(0, 2, " SCHEDULE ")

    stdscr.refresh()



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