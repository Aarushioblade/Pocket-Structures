import copy

from card import Card


class Deck:
    def __init__(self, cards: list[Card] = None):
        self.cards: list[Card] = []
        self.log = None
        if cards is not None: self.cards = cards

    def add_card(self, other: Card, is_below: bool = True) -> int:
        if not isinstance(other, Card): raise TypeError
        new_card = copy.deepcopy(other)
        new_card.log = self.log
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
        print("Core not found")
        print(self.cards)
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
                    # print(f"{test.id} is banned")
                    continue
                distance = abs(index - start_index)
                if local_closest_distance == -1 or distance <= local_closest_distance:
                    local_closest_distance = distance
                    new = test
            if new is None:
                raise ValueError
            new_cards.append(new)
            banned_id.append(new.id)

        # print(f"Closest cards to {card.name}: \n{new_cards}")
        return new_cards

    def __copy__(self) -> Deck:
        new_deck = Deck(self.cards)
        return new_deck
