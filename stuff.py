import copy
from enum import Enum
from math import floor

from color import Color


def colored_type(box_type: Box.Types) -> str:
    return colored_string(box_type, box_type.name)


def colored_string(box_type: Box.Types, value: str) -> str:
    string: str = ""
    string += Box.colors[box_type]
    string += value
    string += Color.WHITE
    return string


class Box:
    class Types(Enum):
        HEALTH = 0
        MATERIAL = 1
        ENERGY = 2
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

    def __str__(self) -> str:
        string: str = "[ "
        for index, stuff in enumerate(self.stuff):
            if not stuff: continue
            string += colored_string(Box.Types(index), f"{stuff} {Box.Types(index).name} ")
        string += "]"
        return string

    def __repr__(self):
        return f"Flow({self.stuff})"

    def __init__(self, health=0, material=0, energy=0, starbit=0, shield=0, boost=0, packed: list[int] = None):
        self.stuff: list[int] = [0] * 6
        if packed:
            self.stuff = packed
            return
        self.stuff[Box.Types.HEALTH.value] = health
        self.stuff[Box.Types.MATERIAL.value] = material
        self.stuff[Box.Types.ENERGY.value] = energy
        self.stuff[Box.Types.STARBIT.value] = starbit
        self.stuff[Box.Types.SHIELD.value] = shield
        self.stuff[Box.Types.BOOST.value] = boost

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


class Flow(Box):

    def __str__(self) -> str:
        string: str = "( "
        for index, stuff in enumerate(self.stuff):
            if not stuff: continue
            if stuff >= 0:
                string += colored_string(Box.Types(index), f"{stuff:+} {Box.Types(index).name} ")
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

    def boosted(self, amount: float):
        percentage: float = amount / 100.0
        modified = [floor(value * percentage) for value in self.stuff]
        return Flow(packed=modified)
