from pynput import keyboard as kb
import random
import time
from enum import Enum
import copy
from math import floor
from colorama import Fore


class Menu(Enum):
    HOME = 0
    SHOP = 1
    SELL = 3
    RESEARCH = 5
    UPGRADE = 7
    SWAP = 9
    SHOP_CONFIRM = 2
    SELL_CONFIRM = 4
    RESEARCH_CONFIRM = 6
    UPGRADE_CONFIRM = 8
    SWAP_CONFIRM = 10


class Color(Enum):
    RED = Fore.LIGHTRED_EX
    YELLOW = Fore.LIGHTYELLOW_EX
    GREEN = Fore.LIGHTGREEN_EX
    CYAN = Fore.LIGHTCYAN_EX
    BLUE = Fore.LIGHTBLUE_EX
    MAGENTA = Fore.LIGHTMAGENTA_EX
    ULTRA_WHITE = Fore.LIGHTWHITE_EX
    WHITE = Fore.RESET
    GRAY = Fore.WHITE
    BLACK = Fore.LIGHTBLACK_EX

    def __radd__(self, other: str) -> str:
        return other + str(self.value)

    def __add__(self, other: str) -> str:
        return str(self.value) + other

    def __str__(self) -> str:
        return self.value


class Box:
    class Types(Enum):
        HEALTH = 0
        MATERIAL = 2
        ENERGY = 1
        STARBIT = 3
        SHIELD = 4
        BOOST = 5

    colors = {
        Types.HEALTH: Color.GREEN,
        Types.MATERIAL: Color.YELLOW,
        Types.ENERGY: Color.BLUE,
        Types.STARBIT: Color.MAGENTA,
        Types.SHIELD: Color.CYAN,
        Types.BOOST: Color.CYAN,
    }

    keybinds = {
        Types.HEALTH: "Q",
        Types.MATERIAL: "E",
        Types.ENERGY: "W",
        Types.STARBIT: "R",
        Types.SHIELD: "T",
        Types.BOOST: "Y",
    }

    @staticmethod
    def colored_string(box_type: Box.Types, value: str) -> str:
        string: str = ""
        string += Box.colors[box_type]
        string += value
        string += Color.WHITE
        return string

    def __str__(self) -> str:
        string: str = "[ "
        for index, stuff in enumerate(self.stuff):
            if not stuff: continue
            string += self.colored_string(Box.Types(index), f"{stuff} {Box.Types(index).name} ")
        string += "]"
        return string

    def __repr__(self):
        return f"Box({self.stuff})"

    def __init__(self, health=0, material=0, energy=0, starbit=0, shield=0, boost=0, packed: list[int] = None):
        self.stuff: list[int] = [0] * len(Box.Types)
        if packed:
            self.stuff = packed
            return
        self.stuff[Box.Types.HEALTH.value] = health
        self.stuff[Box.Types.MATERIAL.value] = material
        self.stuff[Box.Types.ENERGY.value] = energy
        self.stuff[Box.Types.STARBIT.value] = starbit
        self.stuff[Box.Types.SHIELD.value] = shield
        self.stuff[Box.Types.BOOST.value] = boost
        self.type: Box.Types | None = None

    def __copy__(self) -> Box:
        return Box(packed=self.stuff)

    def __deepcopy__(self, memo) -> Box:
        new_box = Box(packed=copy.deepcopy(self.stuff, memo))
        memo[id(self)] = new_box
        return new_box

    # this goes left to right. right to left is not necessarily needed.
    def __iadd__(self, other: Flow) -> Box:
        for i in range(len(self.stuff)):
            self.stuff[i] += other.stuff[i]
        return self

    def __isub__(self, other: Flow) -> Box:
        for i in range(len(self.stuff)):
            self.stuff[i] -= other.stuff[i]
        return self

    def __add__(self, other: Flow) -> Box:
        new_stuff: list[int] = []
        for i in range(len(self.stuff)):
            new_stuff.append(self.stuff[i] + other.stuff[i])
        return Box(packed=new_stuff)

    def __sub__(self, other: Flow) -> Box:
        new_stuff: list[int] = []
        for i in range(len(self.stuff)):
            new_stuff.append(self.stuff[i] - other.stuff[i])
        return Box(packed=new_stuff)

    def __lt__(self, other) -> bool:
        # print(f"My box is {self} and the inflow is {other.box}")
        for box, inflow in zip(self.stuff, other.stuff):
            if box < inflow:
                # print(f"true because {box} < {inflow}")
                return True
        return False

    def __eq__(self, other) -> bool:
        for i in range(len(self.stuff)):
            if not (self.stuff[i] == other.stuff[i]):
                return False
        return True

    def __mod__(self, other: Flow) -> Flow:
        new_flow: list[int] = []
        for i in range(len(self.stuff)):
            shared_value = min(self.stuff[i], other.stuff[i])
            new_flow.append(shared_value)
        return Flow(packed=new_flow)

    def __mul__(self, other: float):
        modified = [floor(value * other) for value in self.stuff]
        return Flow(packed=modified)

    def __getitem__(self, stuff_type: Types) -> int:
        return self.stuff[stuff_type.value]

    def __setitem__(self, stuff_type: Types, value):
        self.stuff[stuff_type.value] = value

    def __neg__(self) -> Flow:
        new_flow: list[int] = []
        for i in range(len(self.stuff)):
            new_flow.append(-self.stuff[i])
        return Flow(packed=new_flow)

    def type_of(self, stuff: Box.Types):
        return self.stuff[stuff.value]

    def separate(self) -> list[Flow]:
        flows: list[Flow] = []
        for i, v in enumerate(Box.Types):
            new_flow: Flow = self.only(v)
            new_flow.type = v
            if new_flow != Flow():
                flows.append(new_flow)
        return flows

    def color(self) -> Color:
        if self.type is None: return Color.WHITE
        if self.stuff[self.type.value] < 0: return Color.RED
        return self.colors[self.type]

    def name(self) -> str:
        if self.type is None: return str(self)
        return self.type.name.lower()

    def value(self) -> str:
        if self.type is None: return str(self)
        value = self.stuff[self.type.value]
        return f"{self.color()}{abs(value)}{Color.WHITE}"

    def accent(self) -> str:
        return f"{self.color()}|{Color.WHITE}"

    def only(self, *types: Box.Types) -> Flow:
        new_stuff: list[int] = []
        for i in range(len(self.stuff)):
            if Box.Types(i) in types:
                new_stuff.append(self.stuff[i])
            else:
                new_stuff.append(0)
        return Flow(packed=new_stuff)

    def without(self, *types: Box.Types) -> Flow:
        new_stuff: list[int] = []
        for i in range(len(self.stuff)):
            if Box.Types(i) in types:
                new_stuff.append(0)
            else:
                new_stuff.append(self.stuff[i])
        return Flow(packed=new_stuff)

    def to_flow(self) -> Flow:
        return Flow(packed=self.stuff)

    def absorb(self, flow: Flow) -> None:
        shield_type = Box.Types.SHIELD.value
        health_type = Box.Types.HEALTH.value
        attack = abs(flow.stuff[health_type])
        max_shield_change = min(self.stuff[shield_type], attack)
        self.stuff[shield_type] -= max_shield_change
        attack -= max_shield_change
        self.stuff[health_type] -= attack
        for i in range(len(self.stuff)):
            if i in [health_type, shield_type]: continue
            self.stuff[i] = max(self.stuff[i] - flow.stuff[i], 0)


class Flow(Box):

    def __str__(self) -> str:
        string: str = "( "
        for index, stuff in enumerate(self.stuff):
            if not stuff: continue
            if stuff >= 0:
                string += self.colored_string(Box.Types(index), f"{stuff:+} {Box.Types(index).name} ")
            else:
                string += Color.RED + f"{stuff:+} {Box.Types(index).name} " + Color.WHITE
        string += ")"
        return string

    def __repr__(self):
        return f"Flow({self.stuff})"

    def __copy__(self) -> Flow:
        return Flow(packed=self.stuff)

    def __deepcopy__(self, memo) -> Box:
        new_flow = Flow(packed=copy.deepcopy(self.stuff, memo))
        memo[id(self)] = new_flow
        return new_flow

    def __sub__(self, other: Box) -> Flow:
        new_stuff: list[int] = []
        for i in range(len(self.stuff)):
            new_stuff.append(self.stuff[i] - other.stuff[i])
        return Flow(packed=new_stuff)

    def __isub__(self, other: Box) -> Flow:
        for i in range(len(self.stuff)):
            self.stuff[i] -= other.stuff[i]
        return self

    # return negative values from the original
    def get_inflow(self) -> Flow:
        values: list[int] = []
        for stuff in self.stuff:
            modified = min(stuff, 0)
            modified = abs(modified)
            values.append(modified)
        return Flow(packed=values)

    def get_outflow(self) -> Flow:
        values: list[int] = []
        for stuff in self.stuff:
            modified = max(stuff, 0)
            modified = abs(modified)
            values.append(modified)
        return Flow(packed=values)

    def to_box(self) -> Box:
        return Box(packed=self.stuff)

    def boosted(self, amount: int):
        percentage: float = amount / 100.0
        modified = [floor(value * percentage) for value in self.stuff]
        return Flow(packed=modified)


class Tracker:
    def __init__(self):
        self.production: Box = Box()
        self.bonus_production: Box = Box()
        self.consumption: Box = Box()
        self.demand: Box = Box()
        self.previous_storage: Box = Box()
        self.potential: Box = Box()
        self.storage: Box = Box()
        self.capacity: Box = Box()

    def reset(self):
        self.production = Box()
        self.bonus_production = Box()
        self.consumption = Box()
        self.demand = Box()
        self.previous_storage = copy.copy(self.storage)


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
        print('\n')
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

    def add(self, text: str, value: str | int, color: Color | None = None):
        self.lines.append(str(text))
        self.colors.append(color)
        self.values.append(str(value))

    def __str__(self) -> str:
        return self.display()

    def display(self, prefix: str | None = None):
        string: str = '\n'
        for text, color, value in zip(self.lines, self.colors, self.values):
            current_width = rl_len(text) + rl_len(value)
            if "-" in value and color: color = Color.RED
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
        self.current_directory: str = "intro"

    def load(self, directory: str):
        if self.current_directory in ["game over", "game complete"]:
            return
        self.current_directory = directory
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

        counter: int = 0
        for line in self.all_lines:
            if counter > 1000: break
            filter_satisfied: bool = False
            keywords: list[str] = ["turn", "constructed", "upgraded", "swapped", "entered"]
            for word in keywords:
                if line.lower().count(word) or line == "":
                    filter_satisfied = True
            if not self.stuff_fiter: filter_satisfied = True

            if not filter_satisfied:
                stuff_satisfied: bool = False
                for stuff in self.stuff_fiter:
                    if line.count(stuff.casefold()):
                        stuff_satisfied = True
                if stuff_satisfied:
                    filter_satisfied = True

            if filter_satisfied:
                filtered_lines.append(line)
            counter += 1

        self.to_pages(filtered_lines)
        return

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


class SummaryPanel(Panel):
    def __init__(self, width: int, tracker: Tracker):
        super().__init__(width)
        self.tracker = tracker

    def rewrite(self):
        self.clear()
        for i in range(len(Box.Types)):
            stuff = Box.Types(i)
            production = self.tracker.production.type_of(stuff)
            bonus_production = self.tracker.bonus_production.type_of(stuff)
            consumption = -self.tracker.consumption.type_of(stuff)
            potential = self.tracker.potential.type_of(stuff)
            demand = -self.tracker.demand.type_of(stuff)
            storage = self.tracker.storage.type_of(stuff)
            capacity = self.tracker.capacity.type_of(stuff)
            if not (production or consumption or storage):
                if not stuff in [Box.Types.HEALTH, Box.Types.MATERIAL, Box.Types.STARBIT, Box.Types.ENERGY]:
                    continue
            stuff_color = Box.colors[stuff]
            self.write(f"\n{stuff_color}{stuff.name}{Color.WHITE}")
            if production > 0: production = f"{production:+}"
            if potential > 0: potential = f"{potential:+}"
            if bonus_production > 0:
                total_production = f"{production}{Color.CYAN}{bonus_production:+}{Color.WHITE}"
            else:
                total_production = production
            info = Info(self.width)
            info.add("Production", total_production, stuff_color)
            if potential != production: info.add("Potential", potential, stuff_color)
            info.add("Consumption", consumption, stuff_color)
            if demand != consumption: info.add("Demand", demand, stuff_color)
            info.add("Storage", storage, stuff_color)
            info.add("Capacity", capacity, stuff_color)
            self.write(info.display())


class Card:
    ID: int = 0

    def __init__(self, name: str, storage: Box, levels: list[Level], priority: int, is_enemy: bool = False,
                 is_interactable: bool = True, is_core: bool = False, requires_enemies: bool = False):
        self.requires_enemies: bool = requires_enemies
        self.name: str = name
        self.storage: Box = storage
        self.levels: list[Level] = levels
        self.priority: int = priority
        self.is_interactable: bool = is_interactable
        self.is_enemy: bool = is_enemy
        self.is_core: bool = is_core
        self.level: int = 1
        self.inflow: Flow = Flow()
        self.outflow: Flow = Flow()
        self.update_flows()
        self.charge: Box = Box()
        self.purchased: Box = Box()
        self.height: int = 12
        self.is_shielded = False
        self.destroyed: bool = False
        self.id: int = Card.ID
        self.log: LogPanel | None = None
        self.tracker: Tracker = Tracker()
        self.action: str | None = None
        Card.ID += 1

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self) -> int:
        return hash((self.name, self.id))

    def __str__(self) -> str:
        # return self.name
        string: str = f"{"Destroyed " if self.destroyed else ""}{self.name}"
        if self.level > 1: string += f" [LVL{self.level}]"
        return string

    def __repr__(self) -> str:
        return f"{self.name} ({self.id})"

    def __copy__(self) -> Card:
        new_card: Card = Card(self.name, self.storage, self.levels, self.priority, self.is_enemy, self.is_interactable,
                              self.is_core, self.requires_enemies)
        new_card.level = self.level
        return new_card

    def __deepcopy__(self, memo) -> Card:
        new_storage: Box = copy.deepcopy(self.storage, memo)
        new_card: Card = Card(self.name, new_storage, self.levels, self.priority, self.is_enemy, self.is_interactable,
                              self.is_core, self.requires_enemies)
        memo[id(self)] = new_card = new_card
        new_card.purchased = copy.deepcopy(self.purchased, memo)
        new_card.charge = copy.deepcopy(self.charge, memo)
        new_card.level = self.level
        return new_card

    def __add__(self, other: Card) -> list[Card]:
        return [self, other]

    def __radd__(self, other: list[Card]) -> list[Card]:
        other.append(self)
        return other

    def write(self, text: str):
        if not self.log: return
        self.log.write(text)

    def level_up(self):
        if self.level == len(self.levels): return
        self.level += 1
        self.update_flows()

    def stats(self) -> Level:
        return self.levels[self.level - 1]

    def next_stats(self):
        return self.levels[self.level]

    def update_flows(self) -> None:
        self.inflow: Flow = self.stats().flow.get_inflow()
        self.outflow: Flow = self.stats().flow.get_outflow()

    def produce(self) -> None:
        self.storage += self.outflow
        if self.outflow == Flow(): return
        # self.write(f"{self.name} produced {self.outflow}")
        self.tracker.production += self.outflow
        for stuff in self.outflow.separate():
            self.write(f"{stuff.accent()} {self} produced {stuff.value()} {stuff.name()}")

    def is_destroyed(self):
        if self.storage.stuff[Box.Types.HEALTH.value] < 0:
            self.storage.stuff[Box.Types.HEALTH.value] = 0
        self.destroyed = self.storage.stuff[Box.Types.HEALTH.value] == 0
        return self.destroyed

    def reset_storage(self) -> None:
        excess: Flow = self.get_excess().without(Box.Types.BOOST)
        if not self.is_shielded:
            excess += self.storage.only(Box.Types.SHIELD) % Flow(shield=50)
        if excess == Flow(): return
        self.storage -= excess
        if self.is_destroyed():
            self.action = f"{Color.GRAY}DESTROYED{Color.WHITE}"
            self.write(f"{Color.RED}{self.name} destroyed!{Color.WHITE}")

    def reset_status(self):
        self.charge = Box()
        self.is_shielded = False
        excess: Flow = self.get_excess().only(Box.Types.BOOST)
        if excess == Flow(): return
        self.storage -= excess

    def get_excess(self):
        excess: Box = self.storage - self.stats().capacity.to_flow()
        return excess.to_flow().get_outflow()

    def collect(self, other: Card) -> None:
        required: Flow = self.inflow - self.charge
        transfer: Flow = other.storage % required.to_flow()
        if transfer == Flow(): return
        other.storage -= transfer
        self.charge += transfer
        self.tracker.consumption += transfer
        for stuff in transfer.separate():
            if stuff.type is None: continue
            inflow = self.stats().flow.get_inflow().stuff[stuff.type.value]
            charge = self.charge.stuff[stuff.type.value]
            if charge < inflow:
                progress = f"{stuff.color()}({charge}/{inflow}){Color.WHITE}"
            else:
                progress = ""
            self.write(f"{stuff.accent()} {self} received {stuff.value()} {stuff.name()} from {other} {progress}")

    def collect_purchase(self, other: Card) -> None:
        required: Flow = self.stats().price.to_flow() - self.purchased
        transfer: Flow = other.storage % required.to_flow()
        if transfer == Flow(): return
        other.storage -= transfer
        self.purchased += transfer
        self.tracker.consumption += transfer
        if self.level == 1:
            for stuff in transfer.separate():
                self.write(f"{stuff.accent()} {other} contributed {stuff.value()} {stuff.name()} to build {self}")
        else:
            for stuff in transfer.separate():
                self.write(f"{stuff.accent()} {other} contributed {stuff.value()} {stuff.name()} to upgrade {self}")

    def collect_research(self, other: Card):
        required: Flow = self.stats().research_cost.to_flow() - self.stats().researched
        transfer: Flow = other.storage % required.to_flow()
        if transfer == Flow(): return
        other.storage -= transfer
        self.stats().researched += transfer
        self.tracker.consumption += transfer
        for stuff in transfer.separate():
            self.write(f"{stuff.accent()} {other} contributed {stuff.value()} {stuff.name()} to research {self}")

    def get_storage_transfer(self, other: Card) -> Flow:
        maximum_to_receive: Box = other.stats().capacity - other.storage.to_flow()
        transfer: Flow = maximum_to_receive.to_flow().get_outflow() % self.get_excess()
        return transfer

    def store(self, other: Card) -> None:
        if other.is_enemy: return
        transfer: Flow = self.get_storage_transfer(other).without(Box.Types.HEALTH, Box.Types.SHIELD, Box.Types.BOOST)
        if transfer == Flow(): return
        self.storage -= transfer
        other.storage += transfer
        for stuff in transfer.separate():
            self.write(f"{stuff.accent()} {other} stored {stuff.value()} {stuff.name()} from {self}")

    def send_to(self, other: Card) -> None:
        flow = self.stats().effect_flow
        if self.is_enemy == other.is_enemy:
            flow = flow.get_outflow()
            other.storage += flow
        else:
            flow = -flow.get_inflow()
            other.storage.absorb(flow)
        if flow == Flow(): return
        if not flow.only(Box.Types.SHIELD) == Flow():
            other.is_shielded = True
        if self.is_enemy:
            self.tracker.consumption -= flow
        else:
            self.tracker.production += flow
        for stuff in flow.separate():
            self.write(f"{stuff.accent()} {self} sent {stuff.value()} {stuff.name()} to {other}")

    def is_charged(self) -> bool:
        return self.charge == self.inflow

    def bonus_produce(self) -> None:
        if not self.is_charged(): return
        boost: int = self.storage.stuff[Box.Types.BOOST.value]
        bonus_flow: Flow = self.outflow.without(Box.Types.BOOST).boosted(boost)
        if bonus_flow == Flow(): return
        self.storage += bonus_flow
        self.tracker.bonus_production += bonus_flow
        for stuff in bonus_flow.separate():
            self.write(f"{stuff.accent()} {self} produced {stuff.value()} extra {stuff.name()}")

    def bonus_send_to(self, other: Card) -> None:
        if not self.is_charged(): return
        boost: int = self.storage.stuff[Box.Types.BOOST.value]
        bonus_flow = self.stats().effect_flow.without(Box.Types.BOOST).boosted(boost)
        if self.is_enemy == other.is_enemy:
            bonus_flow = bonus_flow.get_outflow()
        else:
            bonus_flow = -bonus_flow.get_inflow()
        if bonus_flow == Flow(): return
        other.storage += bonus_flow
        if self.is_enemy:
            self.tracker.consumption -= bonus_flow
        else:
            self.tracker.bonus_production += bonus_flow
        for stuff in bonus_flow.separate():
            self.write(f"{stuff.accent()} {self} sent {stuff.value()} extra {stuff.name()} to {other}")

    def display(self, selected: bool = False, include_name: bool = True, width: int = 30, name_value: str = "") -> Info:
        info = Info(width, prefix="- ")
        if include_name: info.add(str(self), name_value)
        if not selected: return info
        for i in range(len(Box.Types)):
            stuff = Box.Types(i)
            name = stuff.name
            flow = self.stats().flow.stuff[stuff.value]
            effect = self.stats().effect_flow.stuff[stuff.value]
            storage = self.storage.stuff[stuff.value]
            capacity = self.stats().capacity.stuff[stuff.value]
            color = Box.colors[stuff]
            if flow: info.add(f"{name.capitalize()} flow ", f"{flow:+}", color)
            if storage or (capacity and not (Box.Types(i) is Box.Types.SHIELD)):
                info.add(f"{name.capitalize()} ", f"{storage}/{capacity}", color)
            if effect: info.add(f"{name.capitalize()} effect ", f"{effect:+}", color)
        if self.stats().range: info.add("Range", f"{self.stats().range}", Color.WHITE)
        if self.action: info.add("Status", self.action, Color.WHITE)
        return info

    def sell_price(self) -> Flow:
        if self.is_enemy:
            return self.stats().price.to_flow()
        if self.is_destroyed():
            return self.purchased * 0.25
        return self.purchased * 0.75

    def at_max_level(self) -> bool:
        return self.level == len(self.levels)

    def next_level_unlocked(self) -> bool:
        if self.at_max_level(): return False
        return self.next_stats().unlocked

    def health_bar(self) -> str:
        step = 50 if self.is_core else 10
        max_bars = self.stats().capacity.stuff[Box.Types.HEALTH.value] // step
        hp = f"{Color.WHITE.value}["
        if self.storage.stuff[Box.Types.SHIELD.value] > 0:
            filled_bars = self.storage.stuff[Box.Types.SHIELD.value] // step
            filled_color = Color.CYAN.value
            unfilled_color = Color.GREEN.value
        else:
            filled_bars = self.storage.stuff[Box.Types.HEALTH.value] // step
            filled_color = Color.GREEN.value
            unfilled_color = Color.RED.value

        unfilled_bars = max_bars - filled_bars

        hp += unfilled_color
        for i in range(unfilled_bars): hp += "|"
        hp += filled_color
        for i in range(filled_bars): hp += "|"
        hp += f"{Color.WHITE.value}]"
        return hp

    def missing_health(self) -> bool:
        return not self.storage.only(Box.Types.HEALTH) == self.stats().capacity.only(Box.Types.HEALTH)


class Level:
    def __init__(self, level: int, capacity: Box, flow: Flow, price: Box, unlocked: bool = False,
                 effect_range: int = 0, effect_flow: Flow = None, research_cost: Box = None,
                 precondition: list[tuple] = None):
        self.level = level
        self.price: Box = price
        self.capacity: Box = capacity
        self.flow: Flow = flow
        if not effect_flow: effect_flow = Flow()
        self.effect_flow = effect_flow
        self.range: int = effect_range
        self.unlocked: bool = unlocked
        if not research_cost: research_cost: Box = Box()
        self.research_cost: Box = research_cost
        self.researched: Box = Box()
        self.precondition: list[tuple] | None = precondition

    def display(self) -> str:
        return str(self)


class Template(Enum):
    CORE = Card("Core", Box(health=360, starbit=120), [
        Level(1, Box(health=360, material=12, energy=72, starbit=15000, shield=120, boost=0),
              Flow(energy=+6), price=Box(), unlocked=True, effect_range=0, effect_flow=Flow(health=+2)),
        Level(2, Box(health=720, material=36, energy=144, starbit=15000, shield=360, boost=0),
              Flow(energy=+24), price=Box(energy=240, material=132, starbit=300), unlocked=True, effect_range=2,
              effect_flow=Flow(health=+12)),
        Level(3, Box(health=1200, material=96, energy=240, starbit=15000, shield=800),
              Flow(energy=+36), price=Box(energy=600, material=480, starbit=732), unlocked=True, effect_range=4,
              effect_flow=Flow(health=+24, boost=+75)),
    ], priority=0, is_interactable=False, is_core=True)

    MINE = Card("Laser Mine", Box(health=72), [
        Level(1, Box(health=72, shield=72), Flow(material=+3, energy=-8), Box(starbit=18), False,
              research_cost=Box(energy=36)),
        Level(2, Box(health=78, shield=78), Flow(material=+12, energy=-20), Box(starbit=24), False,
              research_cost=Box(starbit=96)),
        Level(3, Box(health=84, shield=84), Flow(material=+64, energy=-32), Box(starbit=30), False,
              research_cost=Box(starbit=180)),
    ], 2)

    FACTORY = Card("Factory", Box(health=72), [
        Level(1, Box(health=72, shield=72), Flow(material=-9, energy=-6, starbit=+7), Box(starbit=24), False,
              research_cost=Box(material=1)),
        Level(2, Box(health=78, shield=78), Flow(material=-24, energy=-15, starbit=+16), Box(starbit=30), False,
              research_cost=Box(starbit=180)),
        Level(3, Box(health=84, shield=84), Flow(material=-72, energy=-45, starbit=+60), Box(starbit=36), False,
              research_cost=Box(starbit=360)),
    ], 3)

    CANNON = Card("Star Cannon", Box(health=132), [
        Level(1, Box(health=132, shield=132), Flow(energy=-6, material=-3), Box(starbit=24), False, 1, Flow(health=-3),
              research_cost=Box(starbit=8)),
        Level(2, Box(health=138, shield=138), Flow(energy=-12, material=-6), Box(starbit=36), False, 2,
              Flow(health=-12),
              research_cost=Box(starbit=72)),
        Level(3, Box(health=144, shield=144), Flow(energy=-24, material=-12), Box(starbit=48), False, 3,
              Flow(health=-36),
              research_cost=Box(starbit=216)),
    ], 5, requires_enemies=True)

    GENERATOR = Card("Generator", Box(health=36), [
        Level(1, Box(health=36, shield=36), Flow(energy=+12), Box(starbit=12), True),
        Level(2, Box(health=42, shield=42), Flow(energy=+36), Box(starbit=16), False,
              research_cost=Box(starbit=15), precondition=[(FACTORY, 1)]),
        Level(3, Box(health=48, shield=48), Flow(energy=+72), Box(starbit=20), False,
              research_cost=Box(starbit=72)),
        Level(4, Box(health=54, shield=54), Flow(energy=+144), Box(starbit=24), False,
              research_cost=Box(starbit=100)),
        Level(5, Box(health=60, shield=60), Flow(energy=+360), Box(starbit=24), False,
              research_cost=Box(starbit=100)),
    ], 1)

    STORAGE = Card("Storage", Box(health=120), [
        Level(1, Box(health=120, material=36, shield=120), Flow(), Box(starbit=12), False,
              research_cost=Box(material=10), precondition=[(FACTORY, 1)]),
        Level(2, Box(health=126, material=120, shield=126), Flow(), Box(starbit=16), False,
              research_cost=Box(starbit=32)),
        Level(3, Box(health=132, material=252, shield=132), Flow(), Box(starbit=84), False,
              research_cost=Box(starbit=120)),
    ], 4)

    POWER_BOX = Card("Power Box", Box(health=120), [
        Level(1, Box(health=120, energy=84, shield=120), Flow(), Box(starbit=12), False,
              research_cost=Box(energy=15), precondition=[(FACTORY, 1)]),
        Level(2, Box(health=126, energy=216, shield=126), Flow(), Box(starbit=16), False,
              research_cost=Box(starbit=32)),
        Level(3, Box(health=132, energy=456, shield=132), Flow(), Box(starbit=84), False,
              research_cost=Box(starbit=120)),
    ], 4)

    HYPERBEAM = Card("Hyperbeam", Box(health=156), [
        Level(1, Box(health=156, shield=156), Flow(energy=-60), Box(starbit=200), False, 2, Flow(health=-20),
              research_cost=Box(starbit=276), precondition=[(CANNON, 1), (POWER_BOX, 1)]),
    ], 5, requires_enemies=True)

    ENEMY = Card("Enemy", Box(health=24), [
        Level(1, Box(health=24, shield=24), Flow(), Box(starbit=48), True, 1, effect_flow=Flow(health=-6)),
        Level(2, Box(health=60, shield=60), Flow(), Box(starbit=108), True, 1, effect_flow=Flow(health=-12)),
        Level(3, Box(health=120, shield=120), Flow(), Box(starbit=192), True, 1, effect_flow=Flow(health=-24)),
    ], 9, is_enemy=True, is_interactable=False)

    REGENERATOR = Card("Regenerator", Box(health=120), [
        Level(1, Box(health=120, shield=120), Flow(material=-12), Box(starbit=264), False, 3, Flow(health=+12),
              research_cost=Box(starbit=372), precondition=[(FACTORY, 1), (STORAGE, 1)]),
        Level(2, Box(health=126, shield=120), Flow(material=-36), Box(starbit=312), False, 4, Flow(health=+36),
              research_cost=Box(starbit=452)),
        Level(3, Box(health=132, shield=120), Flow(material=-72), Box(starbit=408), False, 5, Flow(health=+72),
              research_cost=Box(starbit=452))
    ], 6)

    SHIELD = Card("Shield", Box(health=24), [
        Level(1, Box(health=24, shield=276), Flow(energy=-24), Box(starbit=348), False, 2, Flow(shield=+6),
              research_cost=Box(starbit=564), precondition=[(REGENERATOR, 1)]),
        Level(2, Box(health=30, shield=282), Flow(energy=-48), Box(starbit=444), False, 3, Flow(shield=+12),
              research_cost=Box(starbit=612)),
        Level(3, Box(health=36, shield=288), Flow(energy=-84), Box(starbit=528), False, 4, Flow(shield=+36),
              research_cost=Box(starbit=744)),
    ], 7)

    BOOST = Card("Booster", Box(health=48), [
        Level(1, Box(health=48, shield=48), Flow(energy=-48, material=-2), Box(starbit=456), False, 1, Flow(boost=+50),
              research_cost=Box(starbit=852), precondition=[(SHIELD, 1)]),
        Level(2, Box(health=54, shield=54), Flow(energy=-60, material=-4), Box(starbit=516), False, 1, Flow(boost=+100),
              research_cost=Box(starbit=1284)),
        Level(3, Box(health=60, shield=60), Flow(energy=-96, material=-8), Box(starbit=636), False, 2, Flow(boost=+150),
              research_cost=Box(starbit=1476)),
    ], 8)

    FINALE = Card("Ultimate Megastructure", Box(health=1728), [
        Level(1, Box(health=1728, material=1728, energy=1728, shield=1728),
              Flow(energy=+1728, material=+1728, boost=+1728, shield=+1728, starbit=+1728), Box(starbit=15000), False,
              12, Flow(health=+1728), Box(starbit=15000), precondition=[(BOOST, 1)])
    ], 0)


class Deck:
    def __init__(self, cards: list[Card] = None):
        self.cards: list[Card] = []
        self.log = None
        self.tracker = None
        if cards is not None: self.cards = cards

    def add_card(self, other: Card, is_below: bool = True) -> int:
        if not isinstance(other, Card): raise TypeError
        new_card = copy.deepcopy(other)
        new_card.log = self.log
        new_card.tracker = self.tracker
        if is_below:
            self.cards.append(new_card)
        else:
            self.cards.insert(0, new_card)
        return self.cards.index(new_card)

    def __isub__(self, other: Card) -> Deck:
        try:
            self.cards.remove(other)
        except ValueError:
            pass
        return self

    def __truediv__(self, other: Card) -> Deck:
        excluded_cards: list[Card] = [card for card in self.cards if card != other]
        return Deck(excluded_cards)

    def __mul__(self, other: Card | list[Card]) -> Deck:
        if isinstance(other, list):
            included_cards: list[Card] = [card for card in self.cards if card in other]
        else:
            included_cards: list[Card] = [card for card in self.cards if card == other]
        return Deck(included_cards)

    def __add__(self, other: Deck) -> Deck:
        self.cards.extend(other.cards)
        return self

    def __len__(self) -> int:
        return len(self.cards)

    def __str__(self) -> str:
        string: str = "\n"
        for card in self.cards:
            string += f"{card}\n"
        return string

    def __repr__(self) -> str:
        return f"{self.cards}"

    def __getitem__(self, index: int) -> Card | None:
        try:
            return self.cards[index]
        except IndexError:
            return None

    def __setitem__(self, index: int, value: Card) -> None:
        try:
            self.cards[index] = value
        except IndexError:
            return None

    def __delitem__(self, index: int) -> None:
        try:
            del self.cards[index]
        except IndexError:
            return None

    def in_range(self, other: Card) -> list[Card]:
        if other.is_destroyed(): return [other]
        max_distance = other.stats().range
        cards_in_range: list[Card] = []
        sorted_deck = self.cards  # self.sorted_by_distance(other)
        for x in range(len(sorted_deck)):
            distance = abs(x - sorted_deck.index(other))
            if distance <= max_distance:
                cards_in_range.append(sorted_deck[x])
        return cards_in_range

    def index_with_name(self, card: Card) -> int | None:
        for index, other in enumerate(self.cards):
            if other.name == card.name:
                return index
        return None

    def index_of(self, card: Card) -> int:
        return self.cards.index(card)

    def get_core(self) -> Card:
        for card in self.cards:
            if card.is_core:
                return card
        return self.cards[0]

    def from_id(self, card_id: int) -> Card | None:
        for card in self.cards:
            if card.id == card_id:
                return card
        return None

    def sorted_by_distance(self, card: Card | None = None) -> list[Card]:
        new_cards: list[Card] = []
        banned_id: list[int] = []
        if card is None:
            card = self.get_core()
        start_index = self.cards.index(card)
        for _ in self.cards:
            new = None
            local_closest_distance = -1
            for index, test in enumerate(self.cards):
                if test.id in banned_id:
                    continue
                distance = abs(index - start_index)
                if local_closest_distance == -1 or distance <= local_closest_distance:
                    local_closest_distance = distance
                    new = test
            if new is None:
                raise ValueError
            new_cards.append(new)
            banned_id.append(new.id)

        return new_cards

    def __copy__(self) -> Deck:
        new_deck = Deck(self.cards)
        return new_deck


def color_text(text: str, color: Color) -> str:
    return f"{color.value}{text}{Color.WHITE.value}"


start_time = time.time()


def get_time():
    return time.time() - start_time


class Game:
    def __init__(self, deck: Deck = None):

        self.build_direction: bool = False
        if deck is None: deck = Deck()
        self.deck: Deck = deck
        self.turn = 1
        self.card_index: int = 0
        self.log: LogPanel = LogPanel(56)
        self.deck.log = self.log
        self.tracker: Tracker = Tracker()
        self.deck.tracker = self.tracker
        self.enemy_spawn_rate: float = 0.00

        self.menu: Menu = Menu.HOME

    def enemy_threat(self) -> float:
        maximum_chance = 0.25
        minimum_chance = 0.05
        m = (maximum_chance - minimum_chance) / 15000
        x = self.get_available_box().type_of(Box.Types.STARBIT)
        x += (self.deck.get_core().level - 1) * 100
        chance = m * x + minimum_chance
        return chance

    def get_available_box(self) -> Box:
        available_box = Box()
        for card in self.deck.sorted_by_distance():
            if card.is_destroyed() or card.is_enemy: continue
            available_box += card.storage.to_flow()
        return available_box

    def get_potential(self) -> Box:
        potential = Box()
        for card in self.deck.sorted_by_distance():
            if card.is_destroyed() or card.is_enemy: continue
            potential += card.stats().flow.get_outflow()
        return potential

    def get_capacity(self) -> Box:
        capacity = Box()
        for card in self.deck.sorted_by_distance():
            if card.is_destroyed() or card.is_enemy: continue
            capacity += card.stats().capacity
        return capacity

    def store_to_other_cards(self, card: Card) -> None:
        for other in self.deck.sorted_by_distance(card):
            if other.is_destroyed(): continue
            if other == card: continue
            card.store(other)

    def collect_from_other_cards(self, card: Card) -> None:
        for other in self.deck.sorted_by_distance(card):
            if other.is_destroyed(): continue
            card.collect(other)

    def collect_purchase_from_other_cards(self, card: Card) -> None:
        for other in self.deck.sorted_by_distance():
            if other.is_destroyed(): continue
            card.collect_purchase(other)

    def collect_research_from_other_cards(self, card: Card) -> None:
        for other in self.deck.sorted_by_distance():
            if other.is_destroyed(): continue
            card.collect_research(other)

    def send_to_other_cards(self, card: Card) -> None:
        for target in self.deck.in_range(card):
            if target.is_destroyed(): continue
            card.send_to(target)

    def bonus_send_to_other_cards(self, card: Card) -> None:
        for target in self.deck.in_range(card):
            if target.is_destroyed(): continue
            card.bonus_send_to(target)

    def calculate(self) -> None | str:

        for card in self.deck.sorted_by_distance():
            card.reset_status()

        for priority in range(0, 10):
            for card in self.deck.sorted_by_distance():
                if card.is_destroyed(): continue
                if card.priority != priority: continue
                if card.requires_enemies:
                    if not self.enemies_in_range(card):
                        card.action = "IDLE"
                        continue
                if card.stats().effect_flow.get_outflow().only(Box.Types.HEALTH) != Flow():
                    if card.outflow == Flow():
                        healing: bool = False
                        for other in self.deck.in_range(card):
                            if other.storage.only(Box.Types.HEALTH) < other.stats().capacity.only(Box.Types.HEALTH):
                                healing = True
                        if not healing:
                            card.action = "IDLE"
                            continue
                self.tracker.demand += card.inflow
                if self.get_available_box() < card.inflow:
                    card.action = color_text("LACK RESOURCES", Color.RED)
                    required: Box = self.get_available_box() - card.inflow
                    required: Flow = -required.to_flow().get_inflow()
                    for stuff in required.separate():
                        self.log.write(f"{stuff.accent()} {card} requires {stuff.value()} {stuff.name()}")
                    continue
                if card.is_enemy:
                    card.action = color_text("HOSTILE", Color.RED)
                else:
                    card.action = "ACTIVE"
                self.collect_from_other_cards(card)
                self.send_to_other_cards(card)
                card.produce()
                self.store_to_other_cards(card)

        for card in self.deck.sorted_by_distance():
            if card.is_destroyed(): continue
            self.bonus_send_to_other_cards(card)
            card.bonus_produce()
            self.store_to_other_cards(card)

        for card in self.deck.sorted_by_distance():
            card.reset_storage()

        for index, card in enumerate(self.deck.cards):
            if not card.is_enemy: continue
            if card.is_destroyed(): continue
            core_index = self.deck.index_of(self.deck.get_core())
            if index < core_index:
                direction = +1
            else:
                direction = -1
            other = self.deck.cards[index + direction]
            if other.is_destroyed() and not other.is_core:
                self.swap(index, index + direction)

        self.enemy_spawn_rate = self.enemy_threat()
        if random.random() < self.enemy_spawn_rate:
            self.add_enemy()

        self.tracker.storage = self.get_available_box()
        self.tracker.potential = self.get_potential()
        self.tracker.capacity = self.get_capacity()

        if self.deck.get_core().is_destroyed():
            game_over_message = f"{Color.MAGENTA.value}CORE DESTROYED - GAME OVER! Time - {get_time():.2f}s {Color.WHITE.value}"
            return game_over_message
        for card in self.deck.cards:
            if card.name == "Ultimate Megastructure":
                win_message = (f"{Color.MAGENTA.value}CONGRATULATIONS - YOU HAVE BUILT THE ULTIMATE MEGASTRUCTURE"
                               f" AND WON THE GAME! Time - {get_time():.2f}s {Color.WHITE.value}")
                return win_message

        self.log.write(f"\n>> TURN {self.turn}\n")
        self.turn += 1

        return None

    def can_buy(self, price: Box) -> bool:
        return not self.get_available_box() < price

    def buy(self, card: Card) -> None:
        if not self.can_buy(card.stats().price):
            raise Exception(f"Can't buy {card.name} for {card.stats().price}")
        card.log = self.log
        card.tracker = self.tracker
        self.collect_purchase_from_other_cards(card)
        self.card_index = self.deck.add_card(card, is_below=self.build_direction)
        self.log.write(f"| Constructed {card}")

    def sell(self, index: int) -> None:
        card = self.deck.cards[index]
        sell_price: Box = card.sell_price()
        for stuff in sell_price.separate():
            self.log.write(f"{stuff.accent()} {card} was sold for {stuff.value()} {stuff.name()}")
        card.storage += sell_price
        self.tracker.production += sell_price
        self.store_to_other_cards(card)
        del self.deck.cards[index]
        if not self.card_index in range(len(self.deck.cards)):
            self.card_index = self.deck.cards.index(self.deck.get_core())

    def can_upgrade(self, index: int) -> bool:
        card = self.deck.cards[index]
        if card.is_enemy: return False
        if card.level == len(card.levels):
            return False
        if not card.next_stats().unlocked:
            return False
        if self.get_available_box() < card.next_stats().price:
            return False
        return True

    def upgrade(self, index: int) -> None:
        card = self.deck.cards[index]
        if not self.can_upgrade(index):
            raise Exception(f"Can't upgrade {card}!")
        card_value = card.purchased.to_flow()
        card.purchased = Box()
        previous_card = str(card)
        card.level_up()
        self.collect_purchase_from_other_cards(card)
        card.purchased += card_value
        self.log.write(f"| Upgraded {previous_card} to [LVL{card.level}]")

    def upgrade_enemy(self, index: int) -> None:
        card = self.deck.cards[index]
        card.level_up()

    def can_research(self, card: Card) -> bool:
        return not self.get_available_box() < card.stats().research_cost

    def research(self, card: Card) -> None:
        if not self.can_research(card):
            raise Exception(f"Can't research {card.name}!")
        levelled_card = copy.deepcopy(card)
        levelled_card.log = self.log
        levelled_card.tracker = self.tracker
        self.collect_research_from_other_cards(levelled_card)
        card.stats().unlocked = True
        if card.stats().level == 1:
            self.log.write(f"| {card.name} can now be constructed!")
        else:
            self.log.write(f"| {card.name} can now be upgraded to [LVL{card.stats().level}]")

    def swap(self, i: int, j: int) -> None:
        temp: Card = self.deck.cards[i]
        self.deck.cards[i] = self.deck.cards[j]
        self.deck.cards[j] = temp
        self.log.write(f"| Swapped {self.deck.cards[j]} with {self.deck.cards[i]}")

    def change_card_index(self, amount: int) -> None:
        self.card_index += amount
        if self.card_index not in range(len(self.deck.cards)):
            self.card_index -= amount

    def set_build_direction(self, direction: bool) -> None:
        self.build_direction = direction

    def display(self, menu: Menu) -> str:
        string: str = ""
        in_shop: bool = menu is Menu.SHOP or menu is Menu.SHOP_CONFIRM
        if in_shop and not self.build_direction:
            string += "+ Preview \n"
        selected_card: Card = self.deck.cards[self.card_index]
        cards_in_range: list[Card] = self.deck.in_range(selected_card)
        for index, card in enumerate(self.deck.cards):
            selected = index == self.card_index
            if menu is Menu.SELL or menu is Menu.SELL_CONFIRM:
                if (card.is_destroyed() or not card.is_enemy) and not card.is_core:
                    value = str(card.sell_price().to_box())
                elif card.is_enemy:
                    value = "ENEMY"
                else:
                    value = "CORE"
            elif menu is Menu.UPGRADE or menu is Menu.UPGRADE_CONFIRM:
                if card.is_enemy:
                    value = "ENEMY"
                elif card.at_max_level():
                    value = "MAX LEVEL"
                elif not card.next_level_unlocked():
                    value = "LOCKED"
                else:
                    value = str(card.next_stats().price)
            else:
                if selected or card.missing_health():
                    value = card.health_bar()
                else:
                    value = ""
            prefix: str = "- "
            if selected: prefix = "= "
            if card.is_destroyed():
                prefix = color_text(prefix, Color.GRAY)
            if card.is_enemy or card.action.count(Color.RED.value):
                prefix = color_text(prefix, Color.RED)
            elif card.is_core:
                prefix = color_text(prefix, Color.WHITE)
            elif card in cards_in_range:
                for stuff in selected_card.stats().effect_flow.separate():
                    prefix = color_text(prefix, stuff.color())

            string += card.display(selected, width=48, name_value=value).display(prefix) + '\n'

        if in_shop and self.build_direction:
            string += "+ Preview \n"
        string = string.rstrip()
        self.menu = menu
        return string

    def add_enemy(self):
        enemy = self.deck.add_card(Template.ENEMY.value, random.choice([True, False]))
        self.card_index = enemy
        enemy_card = self.deck.cards[enemy]
        enemy_card.purchased = enemy_card.stats().price * 4
        upgrade_chance = 1.0 * self.enemy_threat()
        for i in range(len(enemy_card.levels)):
            if random.random() < upgrade_chance:
                self.upgrade_enemy(self.card_index)
            else:
                break
        enemy_card.storage += enemy_card.stats().capacity.only(Box.Types.HEALTH) - enemy_card.storage.only(
            Box.Types.HEALTH)
        self.log.write(f"{Color.RED.value}{enemy_card} has entered the base! {Color.WHITE.value}")

    def enemies_in_range(self, card: Card) -> bool:
        for other in self.deck.in_range(card):
            if other.is_enemy:
                if not other.is_destroyed():
                    return True
        return False


class Shop:
    def __init__(self) -> None:
        self.inventory: list[Card] = []
        self.index: int = 0
        self.update()

    def update(self):
        self.inventory.clear()
        for card in Template:
            if not card.value.is_interactable: continue
            if not card.value.stats().unlocked: continue
            self.inventory.append(card.value)
        self.index = 0

    @staticmethod
    def meets_precondition(level: Level) -> bool:
        if not level.precondition: return True
        for required_card, required_level in level.precondition:
            if not required_card.levels[required_level - 1].unlocked: return False
        return True

    def change_index(self, index: int) -> str:
        self.index += index
        if self.index not in range(len(self.inventory)):
            self.index -= index
        card = self.inventory[self.index]
        return self.select_message(card)

    def selected_card(self) -> Card:
        return copy.deepcopy(self.inventory[self.index])

    def display(self) -> str:
        info = Info(50)
        for index, card in enumerate(self.inventory):
            info.extend(card.display(index == self.index, name_value=str(card.stats().price)))
        return "SHOP\n\n" + info.display()

    def select_message(self, card: Card) -> str:
        # card = self.inventory[self.index]
        return f"Buying {card} for {card.stats().price}"


class Research(Shop):
    def update(self):
        self.inventory.clear()
        for card in Template:
            if not card.value.is_interactable: continue
            for level in card.value.levels:
                if level.unlocked: continue
                if not self.meets_precondition(level): break
                levelled_card = copy.deepcopy(card.value)
                levelled_card.level = level.level
                self.inventory.append(levelled_card)
                break
        self.index = 0

    def completed(self) -> bool:
        return len(self.inventory) == 0

    def display(self) -> str:
        info = Info(50)
        for index, card in enumerate(self.inventory):
            info.extend(card.display(index == self.index, name_value=str(card.stats().research_cost)))
        return "RESEARCH\n\n" + info.display()

    def select_message(self, card: Card) -> str:
        return f"Researching {card} for {card.stats().research_cost}"


menu: Menu = Menu.HOME
game = Game()
game.deck.add_card(Template.CORE.value)
shop = Shop()
research = Research()
shop.update()
research.update()
display = Display()
display.separator = " | "
display.height = 41
home_panel = Panel(50)
shop_panel = Panel(50)
info_panel = InfoPanel(35)
summary_panel = SummaryPanel(23, game.tracker)
display.add(info_panel, home_panel, summary_panel, shop_panel, game.log)
structure_to_swap: Card | None = None
shift_held: bool = False
game_started: bool = False
caption: str = ""
game_complete: bool = False

info_panel.load("intro")
shop_panel.hide()
game.log.hide()


def move(direction: int):
    global caption
    if menu is Menu.HOME:
        game.change_card_index(direction)
        card = game.deck.cards[game.card_index]
        info_panel.load(card.name)
    elif menu is Menu.SHOP:
        caption = shop.change_index(direction)
        shop_panel.clear()
        shop_panel.write(shop.display())
        shop_panel.write('\n')
        shop_panel.set(caption)
        info_panel.load(shop.selected_card().name)
    elif menu is Menu.RESEARCH:
        caption = research.change_index(direction)
        shop_panel.clear()
        shop_panel.write(research.display())
        shop_panel.write('\n')
        shop_panel.set(caption)
        info_panel.load(research.selected_card().name)
    elif menu is Menu.SELL:
        game.change_card_index(direction)
        card = game.deck.cards[game.card_index]
        if card.is_interactable or card.is_destroyed():
            caption = f"Selling {card} for {card.sell_price()}"
        else:
            if card.is_enemy:
                caption = f"Defeat it first!"
            elif card.is_core:
                caption = f"You can't sell the core..."
            else:
                caption = f"This structure cannot be sold"
        shop_panel.set(caption)
        info_panel.load(card.name)
    elif menu is Menu.UPGRADE:
        game.change_card_index(direction)
        card = game.deck.cards[game.card_index]
        if card.at_max_level():
            caption = f"{card} cannot be levelled up any further"
        elif not card.next_level_unlocked():
            caption = f"{card} has not unlocked [LVL{card.level + 1}]"
        elif not card.is_enemy:
            caption = f"{card} -> [LVL{card.next_stats().level}] for {card.next_stats().price}"
        else:
            caption = f"Please do not upgrade {card}"
        shop_panel.set(caption)
        info_panel.load(card.name)
    elif menu is Menu.SWAP:
        game.change_card_index(direction)
        card = game.deck.cards[game.card_index]
        shop_panel.clear()
        if card.is_destroyed() or not card.is_interactable:
            if structure_to_swap:
                shop_panel.write("Swap")
                shop_panel.write(structure_to_swap.display(True).display())
            caption = f"SWAP: {card} cannot be moved"
        else:

            shop_panel.write("Swap")
            if structure_to_swap and structure_to_swap != card:
                caption = f"SWAP: Swap {structure_to_swap} with {card}"
                shop_panel.write(structure_to_swap.display(True).display())
                shop_panel.write("with")
            else:
                caption = f"SWAP: Swap {card}"
            shop_panel.write(card.display(True).display())
        shop_panel.write("\n")
        shop_panel.set(caption)
        info_panel.load(card.name)


def switch_direction(direction: int):
    if menu is Menu.SHOP:
        direction = False if direction == -1 else True
        game.set_build_direction(direction)
    elif not game.log.hidden:
        game.log.flip_page(direction)


message: str | None = None


def exit_menu():
    set_menu(menu.HOME)
    global structure_to_swap
    structure_to_swap = None
    shop_panel.clear()
    shop_panel.hide()
    global caption
    caption = ""
    global message
    global game_complete
    if not game_complete:
        message = game.calculate()
        summary_panel.rewrite()
        game.tracker.reset()
        if message:
            game_complete = True
            if message.lower().count("game over"):
                info_panel.load("game over")
                on_press(kb.Key.enter)
            elif message.lower().count("congratulations"):
                info_panel.load("game complete")
                on_press(kb.Key.enter)


def space():
    global caption
    global structure_to_swap
    match menu:
        case Menu.HOME:
            exit_menu()

        case Menu.SHOP:
            if game.can_buy(shop.selected_card().stats().price):
                set_menu(Menu.SHOP_CONFIRM)
                caption = f"CONFIRM: You are buying {shop.selected_card()}"
            else:
                caption = f"Cannot buy {shop.selected_card()}!"
            shop_panel.set(caption)

        case Menu.SHOP_CONFIRM:
            game.buy(shop.selected_card())
            exit_menu()

        case Menu.SELL:
            card = game.deck.cards[game.card_index]
            if card.is_interactable or card.is_destroyed():
                set_menu(Menu.SELL_CONFIRM)
                caption = f"CONFIRM: You are selling {card}"
            else:
                caption = f"Cannot sell {card}!"
            shop_panel.set(caption)

        case Menu.SELL_CONFIRM:
            game.sell(game.card_index)
            exit_menu()

        case Menu.RESEARCH:
            if research.completed():
                caption = f"Congratulations! You have completed all available research!"
                shop_panel.set(caption)
                return
            card = research.selected_card()
            if game.can_research(card):
                set_menu(Menu.RESEARCH_CONFIRM)
                caption = f"CONFIRM: You are researching {card}"
            else:
                caption = f"Cannot research {card}!"
            shop_panel.set(caption)

        case Menu.RESEARCH_CONFIRM:
            game.research(research.selected_card())
            research.update()
            shop.update()
            exit_menu()

        case Menu.UPGRADE:
            card = game.deck.cards[game.card_index]
            if game.can_upgrade(game.card_index):
                set_menu(Menu.UPGRADE_CONFIRM)
                caption = f"CONFIRM: You are upgrading {card} to [LVL{card.next_stats().level}]"
            else:
                caption = f"Cannot upgrade {card}!"
            shop_panel.set(caption)

        case Menu.UPGRADE_CONFIRM:
            game.upgrade(game.card_index)
            exit_menu()

        case Menu.SWAP:
            global structure_to_swap
            card = game.deck.cards[game.card_index]
            if card.is_destroyed() or not card.is_interactable:
                caption = f"{card} cannot be moved"
            elif structure_to_swap:
                set_menu(Menu.SWAP_CONFIRM)
                caption = f"CONFIRM: You are swapping {card} with {structure_to_swap}"
            else:
                structure_to_swap = card
                caption = f"Select another card to swap {card} with"
            shop_panel.set(caption)

        case Menu.SWAP_CONFIRM:
            swap_index = game.deck.index_of(structure_to_swap)
            game.swap(swap_index, game.card_index)
            exit_menu()


def back():
    global caption
    caption = ""
    match menu:
        case menu.SHOP_CONFIRM:
            shop_menu()
        case menu.SELL_CONFIRM:
            sell_menu()
        case menu.RESEARCH_CONFIRM:
            research_menu()
        case menu.UPGRADE_CONFIRM:
            upgrade_menu()
        case _:
            set_menu(Menu.HOME)
            shop_panel.clear()
            shop_panel.hide()
    move(0)


def set_menu(new_menu: Menu):
    global menu
    menu = new_menu


def shop_menu():
    if game_complete: return
    set_menu(menu.SHOP)
    shop_panel.clear()
    shop_panel.show()
    shop_panel.write(shop.display())
    move(0)


def sell_menu():
    if game_complete: return
    set_menu(menu.SELL)
    shop_panel.clear()
    shop_panel.show()
    shop_panel.write("Select a structure to sell")
    move(0)


def research_menu():
    if game_complete: return
    set_menu(menu.RESEARCH)
    shop_panel.clear()
    shop_panel.show()
    shop_panel.write(research.display())
    move(0)


def upgrade_menu():
    if game_complete: return
    set_menu(menu.UPGRADE)
    shop_panel.clear()
    shop_panel.show()
    shop_panel.write("Select a structure to upgrade")
    move(0)


def swap_menu():
    if game_complete: return
    set_menu(menu.SWAP)
    shop_panel.clear()
    shop_panel.show()
    global structure_to_swap
    structure_to_swap = None
    shop_panel.write("Select a structure to swap")
    move(0)


def summary_menu():
    summary_panel.hidden = not summary_panel.hidden


def log_menu():
    game.log.hidden = not game.log.hidden
    # game.log.add_stuff_filter(Box.Types.STARBIT.name)
    # game.log.clear_filters()


def help_menu():
    info_panel.hidden = not info_panel.hidden


def show_key_actions():
    global game_complete
    string: str = ""
    if menu is Menu.HOME:
        string += "[UP/DOWN] Change Selection | "
        if not game_complete:
            string += "[SPACE/ENTER] End Turn | "
            string += "[1] Shop | "
            string += "[2] Sell | "
            string += "[3] Research | "
            string += "[4] Upgrade | "
            string += "[5] Swap | "
        if summary_panel.hidden:
            string += "[6] Show Summary | "
        else:
            string += "[6] Close Summary | "
        if game.log.hidden:
            string += "[7] Show Logs | "
        else:
            string += "[QWERTY] Select Filter | "
            string += "[SHIFT] Multi-Filter | "
            string += "[7] Close Logs | "
        if info_panel.hidden:
            string += "[8] Show Info "
        else:
            string += "[8] Close Info "
    else:
        string += "[UP/DOWN] Change Selection | "
        if menu in [Menu.SHOP_CONFIRM, Menu.SELL_CONFIRM, Menu.RESEARCH_CONFIRM, Menu.UPGRADE_CONFIRM]:
            string += "[SPACE/ENTER] Confirm | "
            string += "[TAB/DELETE] Go Back "
        else:
            match menu:
                case Menu.SHOP:
                    string += "[LEFT/RIGHT] Change build position | "
                    string += "[SPACE/ENTER] Buy | "
                case Menu.SELL:
                    string += "[SPACE/ENTER] Sell | "
                case Menu.RESEARCH:
                    string += "[SPACE/ENTER] Research | "
                case Menu.UPGRADE:
                    string += "[SPACE/ENTER] Upgrade | "

            string += "TAB/DELETE] Home "
    print(string, end="")
    global message
    if message is not None:
        game_complete = True
        print('\n', message, end="", sep="")


keybinds = {
    "UP": kb.Key.up,
    "DOWN": kb.Key.down,
    "LEFT": kb.Key.left,
    "RIGHT": kb.Key.right,
}


def match_key_to_filter(key: str):
    for stuff in Box.Types:
        if Box.keybinds[stuff] == key:
            return stuff
    return None


def change_filter(stuff: Box.Types):
    if stuff.name in game.log.stuff_fiter:
        game.log.rem_stuff_filter(stuff.name)
        return
    if not shift_held:
        game.log.clear_filters()
    game.log.add_stuff_filter(stuff.name)


def on_press(key):
    global game_started
    if not game_started:
        game_started = True
        key = kb.Key.enter
    global menu
    try:
        key = key.char
        if key.isdigit():
            # print(f"digit {key}")
            key = int(key)
            match key:
                case 0:
                    pass
                case 1:
                    shop_menu()
                case 2:
                    sell_menu()
                case 3:
                    research_menu()
                case 4:
                    upgrade_menu()
                case 5:
                    swap_menu()
                case 6:
                    summary_menu()
                case 7:
                    log_menu()
                case 8:
                    help_menu()
        elif key.isalpha():
            key = key.upper()
            # print(f"alpha {key}")
            stuff_filter = match_key_to_filter(key)
            if stuff_filter:
                change_filter(stuff_filter)
    except AttributeError:
        match key:
            case kb.Key.up:
                move(-1)
            case kb.Key.down:
                move(1)
            case kb.Key.left:
                switch_direction(1)
            case kb.Key.right:
                switch_direction(-1)
            case kb.Key.enter | kb.Key.space:
                space()
            case kb.Key.tab | kb.Key.backspace | kb.Key.delete:
                back()
            case kb.Key.esc:
                return False
            case kb.Key.shift | kb.Key.shift_r:
                global shift_held
                shift_held = True
    finally:
        home_panel.clear()
        home_panel.write(game.display(menu))
        display.render()
        show_key_actions()


def on_release(key):
    try:
        global shift_held
        if key in [kb.Key.shift, kb.Key.shift_r]:
            shift_held = False
    except AttributeError:
        pass


print("Press any key to start the game ", end="")

with kb.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
