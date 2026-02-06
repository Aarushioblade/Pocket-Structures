from color import Color


def rl_len(text) -> int:
    length: int = len(text)
    length -= hidden_char_count(text)
    return length


def hidden_char_count(text) -> int:
    count: int = 0
    for color in Color:
        count += text.count(color.value) * 5
    return count


class Display:
    def __init__(self):
        self.width: int = 60
        self.height: int = 30
        self.panels: list[Panel] = []
        self.empty_char: str = " "
        self.separator: str = "|"
        self.spacing: int = 1

    def test(self):
        canvas: str = ""
        for i in range(self.height):
            line: str = ""
            for j in range(self.width):
                line += self.empty_char
            canvas += line + '\n'
        print(canvas)

    def fit_to_width(self, text: str, width: int) -> str:
        if rl_len(text) > width:
            return text[:width] + Color.WHITE.value
        for i in range(width - rl_len(text)):
            text += self.empty_char
        return text

    def render(self):
        lines: list[str] = []
        for i in range(self.height):
            line: str = self.separator
            for panel in self.panels:
                if i not in range(len(panel.lines)):
                    line += self.empty_char * panel.width
                else:
                    line += self.fit_to_width(panel.lines[i], panel.width)
                line += self.separator * self.spacing
            lines.append(line)
        lines.reverse()
        canvas: str = ""
        for line in lines:
            canvas += line + '\n'
        print(canvas)

    def add(self, *panels: Panel):
        for panel in panels:
            self.panels.append(panel)


class Panel:
    def __init__(self, width: int):
        self.width: int = width
        self.lines: list[str] = []

    def write(self, text: str):
        if text.count('\n') == 0:
            self.lines.insert(0, text)
            return
        for line in text.split('\n'):
            self.lines.insert(0, line)

    def clear(self):
        self.lines.clear()


class Info:
    def __init__(self):
        self.name: str = ""
        self.lines: list[str] = []
        self.colors: list[Color] = []

    def add(self, text: str, color: Color = Color.WHITE):
        self.lines.append(text)
        self.colors.append(color)

    def add_info(self, info: Info, color: Color = Color.WHITE):
        for line, color in zip(info.lines, info.colors):
            self.lines.append(line)
            self.colors.append(color)

    def add_tab(self):
        for i, line in enumerate(self.lines):
            self.lines[i] = self.colors[i].value + "| " + Color.WHITE.value + line

    def __str__(self) -> str:
        string: str = ""
        string += self.name
        for line in self.lines:
            string += line + '\n'
        return string


if __name__ == "__main__":
    display = Display()
    display.add(Panel(30))
    display.add(Panel(30))
    display.panels[0].write(f"Hello World!")
    display.panels[1].write(f"{Color.RED.value}Goodbye World!{Color.WHITE.value}")
    display.render()
