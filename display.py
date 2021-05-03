import curses


def display(stdscr):
    curses.curs_set(0)

    max_height, max_width = stdscr.getmaxyx()
    stdscr.addstr(1, 1, "HTTP Monitoring App")
    window_border = stdscr.subwin(max_height-1, max_width, 0, 0)
    window_border.border()
    stdscr.refresh()
    stdscr.getkey()


if __name__ == '__main__':
    curses.wrapper(display)
