import unicodedata


NAME_WIDTH = 8
EVENT_WIDTH = 4


def display_width(text: str) -> int:
    width = 0
    for char in text:
        width += 2 if unicodedata.east_asian_width(char) in {"F", "W"} else 1
    return width


def pad_display(text: str, width: int, align: str = "<") -> str:
    padding = max(0, width - display_width(text))
    if align == ">":
        return " " * padding + text
    if align == "^":
        left = padding // 2
        right = padding - left
        return " " * left + text + " " * right
    return text + " " * padding


def actor_name(name: str) -> str:
    return pad_display(name, NAME_WIDTH)


def event_name(event: str) -> str:
    return pad_display(event, EVENT_WIDTH)
