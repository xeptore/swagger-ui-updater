""" Provide basic colored console print functions
Available types:
*  `print_err` --> prints 'message' with a red color.
*  `warning` --> prints 'message' with a yellow color.
*  `success` -- > prints 'message' with a green color.

All of these bright up 'title' text if provided.
"""


class Intensives:
    Red = 9
    Green = 10
    Yellow = 11
    Blue = 12
    Pink = 13
    Cyan = 14


class Standards:
    Red = 1
    Green = 2
    Yellow = 3
    Blue = 4
    Pink = 5
    Cyan = 6


def print_err(error):
    __print_colored__(foreground_color=Intensives.Red, title="Error", message=error)


def panic(error):
    print_err(error)
    exit(0)


def warning(message):
    __print_colored__(foreground_color=Intensives.Yellow, message=message)


def success(message):
    __print_colored__(foreground_color=Intensives.Green, message=message)


def __print_colored__(foreground_color, message, title=""):
    if len(title) > 0:
        print("\033[1;38;5;{}m{}: \033[0;38;5;{}m{}\033[0;0;0m".format(foreground_color, title, foreground_color, message))
    else:
        print("\033[0;38;5;{}m{}\033[0;0;0m".format(foreground_color, message))
