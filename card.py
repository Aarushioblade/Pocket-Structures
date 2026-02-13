import copy

from color import Color
from display import Info, LogPanel
from stuff import Box, Flow

SHOW_ALL: bool = True


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
        for stuff in self.outflow.separate():
            self.write(f"{stuff.accent()} {self} produced {stuff.value()} {stuff.name()}")

    def is_destroyed(self):
        if self.destroyed: return True
        self.destroyed = self.storage.stuff[Box.Types.HEALTH.value] <= 0
        return self.destroyed

    def reset_storage(self) -> None:
        excess: Flow = self.get_excess().without(Box.Types.BOOST)
        if not self.is_shielded:
            excess += self.storage.only(Box.Types.SHIELD) % Flow(shield=50)
        if excess == Flow(): return
        self.storage -= excess
        # self.write(f"RESET: {self.name} -> {excess} -> Void")
        if self.is_destroyed():
            self.write(f"{Color.RED}{self.name} destroyed!{Color.WHITE}")

    def reset_status(self):
        self.charge = Box()
        self.is_shielded = False
        excess: Flow = self.get_excess().only(Box.Types.BOOST)
        if excess == Flow(): return
        self.storage -= excess
        #self.write(f"RESET: {self.name} -> {excess} -> Void")

    def get_excess(self):
        excess: Box = self.storage - self.stats().capacity.to_flow()
        return excess.to_flow().get_outflow()

    def collect(self, other: Card) -> None:
        required: Flow = self.inflow - self.charge
        transfer: Flow = other.storage % required.to_flow()
        if transfer == Flow(): return
        other.storage -= transfer
        self.charge += transfer
        # self.write(f"{self.name} received {transfer} from {other.name} (X/X)")
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
        if self.level == 1:
            # self.write(f"PURCHASE: {self.name} <- {transfer} <- {other.name}")
            # spent x to build
            for stuff in transfer.separate():
                self.write(f"{stuff.accent()} {other} contributed {stuff.value()} {stuff.name()} to build {self}")
        else:
            # self.write(f"UPGRADE: {self.name} <- {transfer} <- {other.name}")
            # spent x to upgrade
            for stuff in transfer.separate():
                self.write(f"{stuff.accent()} {other} contributed {stuff.value()} {stuff.name()} to upgrade {self}")

    def collect_research(self, other: Card):
        required: Flow = self.stats().research_cost.to_flow() - self.stats().researched
        transfer: Flow = other.storage % required.to_flow()
        if transfer == Flow(): return
        other.storage -= transfer
        self.stats().researched += transfer
        # self.write(f"RESEARCH: {self.name} <- {transfer} <- {other.name}")
        # spent x to research

        for stuff in transfer.separate():
            self.write(f"{stuff.accent()} {other} contributed {stuff.value()} {stuff.name()} to research {self}")

    def get_storage_transfer(self, other: Card) -> Flow:
        maximum_to_receive: Box = other.stats().capacity - other.storage.to_flow()
        transfer: Flow = maximum_to_receive.to_flow().get_outflow() % self.get_excess()
        return transfer

    def store(self, other: Card) -> None:
        if other.is_enemy: return
        transfer: Flow = self.get_storage_transfer(other).without(Box.Types.SHIELD, Box.Types.BOOST)
        if transfer == Flow(): return
        self.storage -= transfer
        other.storage += transfer
        #self.write(f"STORE: {self.name} -> {transfer} -> {other.name}")
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
        # self.write(f"{self.name} produced {bonus_flow} extra ")
        for stuff in self.outflow.separate():
            self.write(f"{stuff.accent()} {self} produced {stuff.value()} extra {stuff.name()} ({boost})")

    def bonus_send_to(self, other: Card) -> None:
        if not self.is_charged(): return
        boost: int = self.storage.stuff[Box.Types.BOOST.value]
        flow = self.stats().effect_flow.without(Box.Types.BOOST).boosted(boost)
        if self.is_enemy == other.is_enemy:
            flow = flow.get_outflow()
        else:
            flow = -flow.get_inflow()
        if flow == Flow(): return
        other.storage += flow
        # self.write(f"{self.name} sent {flow} extra {flow.name()} to {other.name}")
        for stuff in flow.separate():
            self.write(f"{stuff.accent()} {self} sent {stuff.value()} extra {stuff.name()} to {other} ({boost})")

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
                 effect_range: int = 0, effect_flow: Flow = None, research_cost: Box = None):
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

    def __str__(self) -> str:
        string: str = ""
        string += f"| | Capacity: {self.capacity}\n"
        string += f"| | Flow: {self.flow}\n"
        string += f"| | Effect: {self.effect_flow}\n"
        if SHOW_ALL:
            string += f"| | Price: {self.price}\n"
            string += f"| | Researched: {self.researched}\n"
            string += f"| | Research Cost: {self.research_cost}\n"
            string += f"| | Unlocked: {self.unlocked}\n"
            string += f"| | Range: {self.range}\n"
        return string

    def display(self) -> str:
        return str(self)
