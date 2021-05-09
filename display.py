import curses
import threading


class Display(threading.Thread):
    def __init__(self, stats, alerts):
        self.stats = stats
        self.alerts = alerts
        self.stdscr = curses.initscr()

    def display(self):
        curses.curs_set(0)

        max_height, max_width = self.stdscr.getmaxyx()
        self.stdscr.addstr(1, 1, "HTTP Log Monitoring")
        window_border = self.stdscr.subwin(max_height-1, max_width, 0, 0)
        window_border.border()

        self.stdscr.addstr(5, 1, "Stats from the Last 10 Seconds")
        self.stdscr.addstr(6, 1, str(self.stats.count_sections))
        self.stdscr.getkey()
