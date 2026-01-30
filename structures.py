import copy

from stuff import Box, Flow

SHOW_ALL: bool = False


class Deck:
    def __init__(self, cards: list[Card] = None):
        self.cards: list[Card] = []
        if cards is not None: self.cards = cards

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

    def __mul__(self, other: Card) -> Deck:
        included_cards: list[Card] = [card for card in self.cards if card == other]
        return Deck(included_cards)

    def __len__(self) -> int:
        return len(self.cards)

    def __str__(self) -> str:
        string: str = ""
        for card in self.cards:
            string += f"{card}\n"
        return string

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


class Card:
    ID: int = 0

    def __init__(self, name: str, storage: Box, levels: list[Level], priority: int, is_enemy: bool = False,
                 level: int = 1, hidden: bool = False):
        self.name: str = name
        self.storage: Box = storage
        self.levels: list[Level] = levels
        self.priority: int = priority
        self.level: int = level
        self.hidden: bool = hidden
        self.is_enemy: bool = is_enemy

        self.inflow: Flow = Flow()
        self.outflow: Flow = Flow()
        self.update_flows()
        self.height: int = 12
        self.id: int = Card.ID
        Card.ID += 1

    def __eq__(self, other):
        return self.name == other.name and self.id == other.id

    def __hash__(self) -> int:
        return hash((self.name, self.id))

    def __str__(self) -> str:
        string: str = ""
        string += f"{self.name}\n"
        string += f"| Storage: {self.storage}\n"
        for index, level in enumerate(self.levels):
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
        new_card: Card = Card(self.name, self.storage, self.levels, self.priority, self.is_enemy, self.level,
                              self.hidden)
        return new_card

    def __deepcopy__(self, memo) -> Card:
        new_storage: Box = copy.deepcopy(self.storage, memo)
        new_card: Card = Card(self.name, new_storage, self.levels, self.priority, self.is_enemy, self.level,
                              self.hidden)
        memo[id(self)] = new_card = new_card
        return new_card

    def stats(self) -> Level:
        return self.levels[self.level - 1]

    def update_flows(self) -> None:
        self.inflow: Flow = self.stats().flow.get_inflow()
        self.outflow: Flow = self.stats().flow.get_outflow()


class Level:
    def __init__(self, price: int, capacity: Box, flow: Flow, unlocked: bool = False, affect_range: int = 0):
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
    CORE = Card("Core", Box(health=1000), [Level(0, Box(health=1000, energy=60), Flow(energy=6), True)], 0, hidden=True)
    GENERATOR = Card("Generator", Box(health=100), [Level(60, Box(health=100), Flow(energy=12), True)], 1)
