import copy

from stuff import Box, Flow

SHOW_ALL: bool = False

class Deck:
    def __init__(self, cards: list[Card] = None):
        self.cards: list[Card] = []
        if cards is not None: self.cards = cards

    def __iadd__(self, other: Card, is_above: bool = True) -> Deck:
        if not isinstance(other, Card): raise TypeError
        new_card = copy.deepcopy(other)
        if is_above:
            self.cards.append(new_card)
        else:
            self.cards.insert(0, new_card)
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

    def in_range(self, other: Card) -> list[Card]:
        max_distance = other.stats().range
        cards_in_range: list[Card] = []
        sorted_deck = self.cards  # self.sorted_by_distance(other)
        for x in range(len(sorted_deck)):
            distance = abs(x - sorted_deck.index(other))
            if distance <= max_distance:
                cards_in_range.append(sorted_deck[x])
        return cards_in_range

    def sorted_by_distance(self, card: Card) -> list[Card]:
        new_cards: list[Card] = []
        for _ in self.cards:
            closest_distance = 999999999999
            closest_card = card
            for x in range(len(self.cards)):
                if self.cards[x] in new_cards: continue
                distance = abs(x - self.cards.index(card))
                if distance < closest_distance:
                    closest_card = self.cards[x]
                    closest_distance = distance
            new_cards.append(closest_card)
        return new_cards

    def __copy__(self) -> Deck:
        new_deck = Deck(self.cards)
        return new_deck

class Card:
    ID: int = 0

    def __init__(self, name: str, storage: Box, levels: list[Level], priority: int, is_enemy: bool = False,
                 is_hidden: bool = False):
        self.name: str = name
        self.storage: Box = storage
        self.levels: list[Level] = levels
        self.priority: int = priority
        self.is_hidden: bool = is_hidden
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
        new_card: Card = Card(self.name, self.storage, self.levels, self.priority, self.is_enemy, self.is_hidden)
        return new_card

    def __deepcopy__(self, memo) -> Card:
        new_storage: Box = copy.deepcopy(self.storage, memo)
        new_card: Card = Card(self.name, new_storage, self.levels, self.priority, self.is_enemy, self.is_hidden)
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
        if self.outflow == Flow(): return
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
        print(f"STORE: {self.name} -> {transfer} -> {other.name}")

    def send_to(self, other: Card) -> None:
        flow = self.stats().effect_flow
        if not self.is_enemy:
            if other.is_enemy:
                flow = flow.get_inflow()
            else:
                flow = flow.get_outflow()
        else:
            if other.is_enemy:
                flow = flow.get_outflow()
            else:
                flow = flow.get_inflow()
        if flow == Flow(): return
        other.storage += flow
        print(f"SEND: {self.name} -> {flow} -> {other.name}")


class Level:
    def __init__(self, level: int, capacity: Box, flow: Flow, price: int = 0, unlocked: bool = False,
                 effect_range: int = 0, effect_flow: Flow = None):
        self.level = level
        self.price: int = price
        self.capacity: Box = capacity
        self.flow: Flow = flow
        if not effect_flow: effect_flow = Flow()
        self.effect_flow = effect_flow
        self.range: int = effect_range
        self.unlocked: bool = unlocked

    def __str__(self) -> str:
        string: str = ""
        string += f"| | Capacity: {self.capacity}\n"
        string += f"| | Flow: {self.flow}\n"
        string += f"| | Effect: {self.effect_flow}\n"
        if SHOW_ALL:
            string += f"| | Price: {self.price}\n"
            string += f"| | Range: {self.range}\n"
            string += f"| | Unlocked: {self.unlocked}\n"
        return string


class Blueprints:
    CORE = Card("Core", Box(health=1000), [
        Level(1, Box(health=1000, material=30, energy=60, starbit=15000, shield=240, boost=100),
              Flow(energy=6), price=0, unlocked=True, effect_range=1, effect_flow=Flow(health=+5))
    ], priority=0, is_hidden=True)
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
        Level(1, Box(health=120), Flow(energy=-20), 200, True, 2, Flow(health=-20)),
    ], 6)
    ENEMY = Card("Enemy", Box(health=60), [
        Level(1, Box(health=60), Flow(), 80, True, 1, effect_flow=Flow(health=-15)),
    ], 9, is_enemy=True, is_hidden=True)
    BOOST = Card("Boost", Box(health=48), [
        Level(1, Box(health=48), Flow(energy=-20), 400, True, 1, Flow(boost=+50)),
    ], 5)
    REGENERATOR = Card("Regenerator", Box(health=100), [
        Level(1, Box(health=100), Flow(energy=-5), 250, True, 3, Flow(health=+10)),
    ], 7)
    SHIELD = Card("Shield", Box(health=64), [
        Level(1, Box(health=64), Flow(energy=-20), 500, True, 2, Flow(shield=+50)),
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
