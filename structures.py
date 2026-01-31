import copy

from stuff import Box, Flow

SHOW_ALL: bool = False


class Deck:
    def __init__(self, cards: list[Card] = None):
        self.cards: list[Card] = []
        if cards is not None: self.cards = cards

        self.next_card_number = 0
        self.last_id = 0

    def __iadd__(self, other: Card) -> Deck:
        if not isinstance(other, Card): raise TypeError
        self.cards.append(copy.deepcopy(other))
        return self

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
        string: str = ""
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

    def in_range(self, other: Card) -> Deck:
        if other.stats().range:
            pass
        return self

    def __next__(self) -> Card:
        if self.next_card_number >= len(self):
            raise StopIteration
        closest_id: int = 0
        next_card: Card = self.cards[0]
        for card in self.cards:
            if card.id <= self.last_id: continue
            if card.id > closest_id != 0: continue
            closest_id = card.id
            next_card = card
        self.next_card_number += 1
        self.last_id = closest_id
        return next_card

    def __iter__(self) -> Deck:
        self.next_card_number = 0
        self.last_id = 0
        return copy.copy(self)

    def __copy__(self) -> Deck:
        return Deck(self.cards)

class Card:
    ID: int = 0

    def __init__(self, name: str, storage: Box, levels: list[Level], priority: int, is_enemy: bool = False,
                 hidden: bool = False):
        self.name: str = name
        self.storage: Box = storage
        self.levels: list[Level] = levels
        self.priority: int = priority
        self.hidden: bool = hidden
        self.is_enemy: bool = is_enemy

        self.level: int = 1
        self.inflow: Flow = Flow()
        self.outflow: Flow = Flow()
        self.update_flows()
        self.charge: Box = Box()
        self.height: int = 12
        self.id: int = Card.ID
        Card.ID += 1

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self) -> int:
        return hash((self.name, self.id))

    def __str__(self) -> str:
        string: str = ""
        string += f"{self.name}\n"
        string += f"| Storage: {self.storage}\n"
        for index, level in enumerate(self.levels):
            if not (index + 1 == self.level or SHOW_ALL): continue
            string += f"| Level {index + 1}\n"
            string += str(level)
        if SHOW_ALL:
            string += f"| Level: {self.level}\n"
        string += f"| Priority: {self.priority}\n"
        string += f"| ID: {self.id:06}\n"
        return string

    def __repr__(self) -> str:
        return f"{self.name} ({self.id})"

    def __copy__(self) -> Card:
        new_card: Card = Card(self.name, self.storage, self.levels, self.priority, self.is_enemy, self.hidden)
        return new_card

    def __deepcopy__(self, memo) -> Card:
        new_storage: Box = copy.deepcopy(self.storage, memo)
        new_card: Card = Card(self.name, new_storage, self.levels, self.priority, self.is_enemy, self.hidden)
        memo[id(self)] = new_card = new_card
        return new_card

    def __add__(self, other: Card) -> list[Card]:
        return [self, other]

    def __radd__(self, other: list[Card]) -> list[Card]:
        other.append(self)
        return other

    def level_up(self):
        self.level += 1
        self.update_flows()

    def stats(self) -> Level:
        return self.levels[self.level - 1]

    def update_flows(self) -> None:
        self.inflow: Flow = self.stats().flow.get_inflow()
        self.outflow: Flow = self.stats().flow.get_outflow()

    def produce(self) -> None:
        self.storage += self.outflow
        print(f"PRODUCE: {self.name} >> {self.outflow}")

    def reset(self) -> None:
        self.charge = Box()
        excess: Flow = self.get_excess()
        if excess == Flow(): return
        self.storage -= excess
        print(f"RESET: {self.name} -> {excess} -> Void")

    def get_excess(self):
        excess: Box = self.storage - self.stats().capacity.to_flow()
        return excess.to_flow().get_outflow()

    def collect(self, other: Card) -> None:
        required: Flow = self.inflow - self.charge
        transfer: Flow = other.storage % required.to_flow()
        if transfer == Flow(): return
        other.storage -= transfer
        self.charge += transfer
        print(f"COLLECT: {self.name} <- {transfer} <- {other.name}")

    def get_storage_transfer(self, other: Card) -> Flow | None:
        maximum_to_receive: Box = other.stats().capacity - other.storage.to_flow()
        transfer: Flow = maximum_to_receive.to_flow().get_outflow() % self.get_excess()
        if transfer == Flow(): return None
        return transfer

    def store(self, other: Card) -> None:
        transfer: Flow = self.get_storage_transfer(other)
        if transfer is None: return
        self.storage -= transfer
        other.storage += transfer
        print(f"STORE: {self.name} -> {transfer} -> {other.name}")


class Level:
    def __init__(self, level: int, capacity: Box, flow: Flow, price: int, unlocked: bool = False,
                 affect_range: int = 0):
        self.level = level
        self.price: int = price
        self.capacity: Box = capacity
        self.flow: Flow = flow
        self.range: int = affect_range
        self.unlocked: bool = unlocked

    def __str__(self) -> str:
        string: str = ""
        string += f"| | Capacity: {self.capacity}\n"
        string += f"| | Flow: {self.flow}\n"
        if SHOW_ALL:
            string += f"| | Price: {self.price}\n"
            string += f"| | Range: {self.range}\n"
            string += f"| | Unlocked: {self.unlocked}\n"
        return string


class Blueprints:
    CORE = Card("Core", Box(health=1000), [
        Level(1, Box(health=1000, material=30, energy=60, starbit=15000), Flow(health=20, energy=6), 0, True)
    ], 0, hidden=True)
    GENERATOR = Card("Generator", Box(health=100), [
        Level(1, Box(health=100), Flow(energy=12), 60, True),
        Level(2, Box(health=135), Flow(energy=36), 120, False),
        Level(3, Box(health=180), Flow(energy=72), 180, False),
    ], 1)
    MINE = Card("Laser", Box(health=100), [
        Level(1, Box(health=100), Flow(material=+6, energy=-8), 80, True),
        Level(2, Box(health=120), Flow(material=+18, energy=-14), 160, False),
        Level(3, Box(health=140), Flow(material=+64, energy=-32), 340, False),
    ], 2)
    FACTORY = Card("Factory", Box(health=100), [
        Level(1, Box(health=100), Flow(material=-6, energy=-3, starbit=+24), 100, True),
    ], 3)
    STORAGE = Card("Storage", Box(health=120), [
        Level(1, Box(health=120, material=60), Flow(), 150, True),
    ], 4)
    POWER_BOX = Card("Power Box", Box(health=120), [
        Level(1, Box(health=120, energy=80), Flow(), 150, True),
    ], 4)
    # not required to work
    HYPERBEAM = Card("Hyperbeam", Box(health=120), [
        Level(1, Box(health=120), Flow(health=-15, energy=-20), 200, True),
    ], 6)
    ENEMY = Card("Enemy", Box(health=60), [
        Level(1, Box(health=60), Flow(health=-12), 80, True),
    ], 9, True, True)
    BOOST = Card("Boost", Box(health=48), [
        Level(1, Box(health=48), Flow(energy=-20, boost=+50), 400, True),
    ], 5)
    REGENERATOR = Card("Regenerator", Box(health=100), [
        Level(1, Box(health=100), Flow(health=+10, energy=-5), 250, True),
    ], 7)
    SHIELD = Card("Shield", Box(health=64), [
        Level(1, Box(health=64), Flow(energy=-20, shield=+10), 500, True),
    ], 8)
    # don't expect these to work
    DIMENSION = Card("Pocket Dimension", Box(health=0), [
        Level(1, Box(health=0), Flow(energy=-100), 900, True),
    ], 8)
    PARALLEL = Card("Parallel Stacker", Box(health=0), [
        Level(1, Box(health=0), Flow(energy=-110), 1000, True),
    ], 8)
    DESTROYER = Card("Destroyer Base", Box(health=200), [
        Level(1, Box(health=200), Flow(health=-30, energy=-50), 1200, True),
    ], 6)
