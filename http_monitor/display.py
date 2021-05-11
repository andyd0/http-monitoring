import curses
import threading


class Display(threading.Thread):
    """A class used to display data from the consumers using curses

    Attributes:
        reader (LogReader): Used to terminate thread if display is closed
        stats (LogStatsConsumer): Provides stats data to display
        alerts (LogAlertConsumer): Provides alert/recovered messaging
        stdscr (curses): Used for writing to CLI
        thread_terminated (boolean): Flag to kill thread
    """

    def __init__(self, reader, stats, alerts):
        """
        Args:
            reader (LogReader): LogReader class
            stats (LogStatsConsumer): LogStatsConsumer class
            alerts (LogAlertConsumer): LogalertConsumer
        """
        threading.Thread.__init__(self)
        self.reader = reader
        self.stats = stats
        self.alerts = alerts
        self.stdscr = curses.initscr()
        self.thread_terminated = False

    def run(self):
        """
        Starts the thread process and writes to screen the data from the
        consumers
        """
        curses.curs_set(0)
        self.stdscr.nodelay(1)

        max_height, max_width = self.stdscr.getmaxyx()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)

        while not self.thread_terminated:
            self.stdscr.erase()

            self.stdscr.addstr(
                1, 2, "HTTP Log Monitoring App (Press q to Quit)"
            )

            window_border = self.stdscr.subwin(max_height-1, max_width, 0, 0)
            window_border.border()

            self.__display_stats_data()
            self.__display_alerts_data()

            self.stdscr.refresh()

            ch = self.stdscr.getch()
            if ch == ord('q'):
                self.reader.thread_terminated = True
                self.stats.thread_terminated = True
                self.alerts.thread_terminated = True
                self.thread_terminated = True

    def __display_stats_data(self):
        """
        Displays the stats data from the stats consumer
        """
        stats_data = self.stats.updated_stats_data()

        self.stdscr.addstr(4, 2, f'Total Hits: {stats_data["hits"]}')
        self.stdscr.addstr(5, 2, f'Total in Bytes: {stats_data["size"]:,}')

        self.stdscr.addstr(8, 2, "Stats from the Last 10 Seconds:")

        section_size = stats_data.get("section_size")
        section_counts = stats_data.get("section_counts")
        status_counts = stats_data.get("status_counts")

        y = 9
        if status_counts:
            y += 1
            self.stdscr.addstr(y, 2, "Status Code Counts:")
            for line in self.__build_status_lines(status_counts):
                y += 1
                self.stdscr.addstr(y, 2, line)

            y += 3
            self.stdscr.addstr(y, 2, "Top Two Sections:")
            for line in self.__build_top_n_sections(
                        section_size, section_counts
                    ):
                y += 1
                self.stdscr.addstr(y, 2, line)

    def __display_alerts_data(self):
        """
        Displays the alerts data from the alerts consumer
        """
        alert_data = self.alerts.updated_alert_data()
        alert_count = alert_data['alert_count']

        alert_text = "Alert" if alert_count == 1 else "Alerts"

        alert_heading = (
            f'There Has Been {alert_count} {alert_text} Since '
            f'Monitoring Started'
        )

        self.stdscr.addstr(4, 50, alert_heading)

        if 'type' in alert_data:
            if alert_data['type'] == 'alert':
                self.stdscr.addstr(6, 50, "Alert!!!", curses.color_pair(1))
            else:
                self.stdscr.addstr(6, 50, "Recovered", curses.color_pair(2))
            self.stdscr.addstr(7, 50, alert_data['msg_line1'])
            self.stdscr.addstr(8, 50, alert_data['msg_line2'])

    def __build_status_lines(self, counts):
        """
        Takes Status counters to get top n for printing to screen
        """
        lines = []
        for code, count in counts.most_common():
            line = f'{code}: {count}'
            lines.append(line)
        return lines

    def __build_top_n_sections(self, section_size, section_counts, n=2):
        """
        Takes Section counters to get top n for printing to screen
        """
        lines = []
        for section, count in section_counts.most_common(n):
            lines.append(f'Section: {section}')
            lines.append(f'Count: {count}')
            lines.append(f'Total in Bytes: {section_size[section]:,}')
            lines.append(f'\n')
        return lines
