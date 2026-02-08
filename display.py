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
        self.separator: str = " "
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
        # if rl_len(text) > width:
        #    return text[:width] + Color.WHITE.value
        for i in range(width - rl_len(text)):
            text += self.empty_char
        return text

    def render(self):
        lines: list[str] = []
        for i in range(self.height):
            line: str = self.separator
            for panel in self.panels:
                if panel.hidden: continue
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
        self.hidden: bool = False

    def write(self, text: str):
        for line in text.split('\n'):
            self.lines.insert(0, line)

    def clear(self):
        self.lines.clear()

    def show(self):
        self.hidden = False

    def hide(self):
        self.hidden = True


class Info:
    def __init__(self, width: int = 15):
        self.name: str = ""
        self.lines: list[str] = []
        self.colors: list[Color | None] = []
        self.values: list[str] = []
        self.width: int = width
        self.color = Color.WHITE

    def add(self, text: str, value: str, color: Color | None = None):
        self.lines.append(text)
        self.colors.append(color)
        self.values.append(value)

    def __str__(self) -> str:
        string: str = '\n'
        for text, color, value in zip(self.lines, self.colors, self.values):
            current_width = rl_len(text) + rl_len(value)
            if "-" in value: color = Color.RED
            if color is not None:
                current_width += 5
                string += f"{color.value}|    {self.color.value}"
            string += f"{text}"
            if current_width < self.width:
                string += " " * (self.width - current_width)
            if color is not None:
                string += f"{color.value}{value}{self.color.value}"
            else:
                string += value
            string += '\n'
        return string.strip()

    def display(self):
        return str(self)

    def extend(self, other: Info):
        self.lines.extend(other.lines)
        self.colors.extend(other.colors)
        self.values.extend(other.values)


class InfoPanel(Panel):
    def __init__(self, width: int):
        super().__init__(width)

    def load(self, directory: str):
        self.write(f"{directory.upper()}\n")
        with open(f"text files/{directory.lower()}.txt") as file:
            for line in file:
                self.write(line.strip())


class LogPanel(Panel):
    def __init__(self, width: int):
        super().__init__(width)
        self.all_lines: list[str] = []
        self.stuff_filter: str = ""
        self.action_filter: str = ""

    def write(self, text: str):
        for line in text.split('\n'):
            self.all_lines.insert(0, line)
        self.filter()

    def clear(self):
        super().clear()
        self.all_lines.clear()

    def filter(self):
        self.lines.clear()
        for line in self.all_lines:
            if self.stuff_filter:
                if not line.count(self.stuff_filter):
                    continue
            if self.action_filter:
                if not line.count(self.action_filter):
                    continue
            self.lines.append(line)

if __name__ == "__main__":
    display = Display()
    display.add(Panel(30))
    display.add(Panel(30))
    display.panels[0].write(f"Hello World!")
    display.panels[1].write(f"{Color.RED.value}Goodbye World!{Color.WHITE.value}")
    display.render()
