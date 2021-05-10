import curses
import threading


class Display(threading.Thread):
    def __init__(self, reader, stats, alerts):
        threading.Thread.__init__(self)
        self.reader = reader
        self.stats = stats
        self.alerts = alerts
        self.stdscr = curses.initscr()
        self.thread_terminated = False

    def run(self):
        curses.curs_set(0)
        self.stdscr.nodelay(1)

        max_height, max_width = self.stdscr.getmaxyx()
        self.stdscr.addstr(1, 1, "HTTP Log Monitoring App - Press q to exit")
        window_border = self.stdscr.subwin(max_height-1, max_width, 0, 0)
        window_border.border()

        while not self.thread_terminated:
            self.stdscr.addstr(3, 1, "Stats from the Last 10 Seconds")

            section_counts, status_counts = self.stats.updated_stats()

            self.stdscr.addstr(4, 1, str(section_counts))
            self.stdscr.addstr(5, 1, str(status_counts))

            self.stdscr.refresh()

            ch = self.stdscr.getch()
            if ch == ord('q'):
                self.reader.thread_terminated = True
                self.stats.thread_terminated = True
                # self.alerts.thread_terminated = True
                self.thread_terminated = True
