import copy

from color import Color
from stuff import Box


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
        self.height: int = 40
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
                if i not in range(len(panel.get_lines())):
                    line += self.empty_char * panel.width
                else:
                    line += self.fit_to_width(panel.get_lines()[i], panel.width)
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

    def set(self, text: str, index: int = 0):
        self.lines[index] = text

    def get_lines(self) -> list[str]:
        return self.lines


class Info:
    def __init__(self, width: int = 15, prefix: str = ""):
        self.name: str = ""
        self.lines: list[str] = []
        self.colors: list[Color | None] = []
        self.values: list[str] = []
        self.width: int = width
        self.color = Color.WHITE
        self.prefix_default: str = prefix

    def add(self, text: str, value: str, color: Color | None = None):
        self.lines.append(text)
        self.colors.append(color)
        self.values.append(value)

    def __str__(self) -> str:
        return self.display()

    def display(self, prefix: str | None = None):
        string: str = '\n'
        for text, color, value in zip(self.lines, self.colors, self.values):
            current_width = rl_len(text) + rl_len(value)
            if "-" in value: color = Color.RED
            if color is not None:
                current_width += 5
                string += " " * rl_len(self.prefix_default)
                string += f"{color.value}|    {self.color.value}"
            else:
                if prefix:
                    string += prefix
                else:
                    string += self.prefix_default
            string += f"{text}"
            if current_width < self.width:
                string += " " * (self.width - current_width)
            if color is not None:
                string += f"{color.value}{value}{self.color.value}"
            else:
                string += value
            string += '\n'
        return string.strip()

    def add_margin(self, width: int):
        pass

    def extend(self, other: Info):
        self.lines.extend(other.lines)
        self.colors.extend(other.colors)
        self.values.extend(other.values)


class InfoPanel(Panel):
    def __init__(self, width: int):
        super().__init__(width)

    def load(self, directory: str):
        self.clear()
        self.write(f"{directory.upper()}\n")
        with open(f"text files/{directory.lower()}.txt") as file:
            for line in file:
                self.write(line.strip())


class LogPanel(Panel):
    def __init__(self, width: int):
        super().__init__(width)
        self.page: int = 0
        self.page_length: int = 30
        self.pages: list[list[str]] = []
        self.all_lines: list[str] = []
        self.stuff_fiter: list[str] = []
        self.action_filter: list[str] = []
        self.to_pages([])

    def write(self, text: str):
        for line in text.split('\n'):
            self.all_lines.insert(0, line)
        self.filter()

    def clear(self):
        self.all_lines.clear()

    def add_stuff_filter(self, stuff: str):
        self.stuff_fiter.append(stuff)
        self.filter()

    def add_action_filter(self, stuff: str):
        self.action_filter.append(stuff)
        self.filter()

    def clear_filters(self):
        self.stuff_fiter.clear()
        self.action_filter.clear()
        self.filter()

    def filter(self):
        filtered_lines: list[str] = []

        for line in self.all_lines:
            filter_satisfied: bool = False
            keywords: list[str] = ["turn", "constructed", "upgraded", "swapped", "entered"]
            for word in keywords:
                if line.casefold().count(word) or line == "":
                    filter_satisfied = True

            stuff_satisfied: bool = not self.stuff_fiter
            action_satisfied: bool = not self.action_filter
            for stuff in self.stuff_fiter:
                if line.count(stuff.casefold()):
                    stuff_satisfied = True
            for action in self.action_filter:
                if line.count(action.upper()):
                    action_satisfied = True

            if stuff_satisfied and action_satisfied:
                filter_satisfied = True

            if filter_satisfied:
                filtered_lines.append(line)

        self.to_pages(filtered_lines)
        return

        without_repeats: list[str] = []

        for i in range(len(filtered_lines) - 1):
            if filtered_lines[i + 1].count("Turn") and filtered_lines[i].count("Turn"): continue
            without_repeats.append(filtered_lines[i])
        if not filtered_lines[-1].count("Turn"): without_repeats.append(filtered_lines[-1])
        self.to_pages(without_repeats)

    def flip_page(self, amount: int):
        self.page += amount
        if not self.page in range(len(self.pages)):
            self.page -= amount

    def to_pages(self, filtered_lines: list[str]):
        current_page: list[str] = []
        self.pages.clear()
        for line in filtered_lines:
            current_page.append(line)
            if len(current_page) > self.page_length:
                self.pages.append(copy.copy(current_page))
                current_page.clear()
        self.pages.append(current_page)
        self.flip_page(0)

    def get_lines(self) -> list[str]:
        try:
            new_lines: list[str] = copy.deepcopy(self.pages[self.page])
        except IndexError:
            print("INVALID PAGE")
            return []
        new_lines.insert(0, "")
        stuff_filters: str = ""
        for i in range(len(Box.Types)):
            stuff = Box.Types(i)
            if stuff.name.upper() in self.stuff_fiter:
                stuff_filters += Box.colors[stuff]
            else:
                stuff_filters += Color.BLACK.value
            stuff_filters += f"[{stuff.name.upper()}] "
        stuff_filters += Color.WHITE.value
        new_lines.insert(0, "Filters: ")
        new_lines.insert(0, stuff_filters)
        new_lines.insert(0, f"Page {len(self.pages) - self.page}/{len(self.pages)}")
        return new_lines

    def rem_stuff_filter(self, stuff: str):
        self.stuff_fiter.remove(stuff)
        self.filter()


if __name__ == "__main__":
    display = Display()
    display.add(Panel(30))
    display.add(Panel(30))
    display.panels[0].write(f"Hello World!")
    display.panels[1].write(f"{Color.RED.value}Goodbye World!{Color.WHITE.value}")
    display.render()
