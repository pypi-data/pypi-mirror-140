__version__ = '0.1.0'

def rgb(r, g, b, text):
    return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, text)

class text:
    black = "\033[0;30m"
    red = "\033[0;31m"
    yellow = "\033[0;33m"
    green = "\033[0;32m"
    blue = "\033[0;34m"
    purple = "\033[0;35m"
    color_reset = "\033[0m"

class bg:
    white_bg = "\x1b[6;30;47m"
    red_bg = "\x1b[6;30;41m"
    yellow_bg = "\x1b[6;30;43m"
    green_bg = "\x1b[6;30;42m"
    blue_bg = "\x1b[6;30;46m"
    purple_bg = "\x1b[6;30;45m"
    color_reset = "\033[0m"

class textmods:
    underline = "\033[0;4m"
    italic = "\033[3m"