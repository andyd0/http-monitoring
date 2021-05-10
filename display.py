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
        self.stdscr.addstr(1, 2, "HTTP Log Monitoring App - Press q to exit")
        window_border = self.stdscr.subwin(max_height-1, max_width, 0, 0)
        window_border.border()
        alert_count = 0

        while not self.thread_terminated:
            stats_data = self.stats.updated_total_stats()

            self.stdscr.addstr(4, 2, f'Total hits: {stats_data["hits"]}')
            self.stdscr.addstr(5, 2, f'Total size in bytes: {stats_data["size"]}')

            self.stdscr.addstr(9, 2, "Stats from the Last 10 Seconds:")

            section_counts, status_counts = self.stats.updated_counts()

            y = 10
            if section_counts and status_counts:
                y += 1
                self.stdscr.addstr(y, 2, "Status Code Counts:")
                lines = self.build_top_n(status_counts)
                for line in lines:
                    y += 1
                    self.stdscr.addstr(y, 2, line)

                y += 4
                self.stdscr.addstr(y, 2, "Top Sections:")
                lines = self.build_top_n(section_counts)
                for line in lines:
                    y += 1
                    self.stdscr.addstr(y, 2, line)

            alert_data = self.alerts.updated_alert_data()

            alert_text = "alert" if alert_data['alert_count'] == 1 else "alerts"

            alert_heading_line1 = f'There has been {alert_count} {alert_text} since'
            alert_heading_line2 = f'monintoring started'
            self.stdscr.addstr(4, 50, alert_heading_line1)
            self.stdscr.addstr(5, 50, alert_heading_line2)

            if 'msg_line1' in alert_data:
                self.stdscr.addstr(7, 50, alert_data['msg_line1'])
                self.stdscr.addstr(8, 50, alert_data['msg_line2'])

            self.stdscr.refresh()

            ch = self.stdscr.getch()
            if ch == ord('q'):
                self.reader.thread_terminated = True
                self.stats.thread_terminated = True
                self.alerts.thread_terminated = True
                self.thread_terminated = True

    def build_top_n(self, counts, n=3):
        lines = []
        for code, count in counts.most_common(n):
            line = f'{code}: {count}'
            lines.append(line)
        return lines
