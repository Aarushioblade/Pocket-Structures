import copy

from card import Card
from deck import Deck
from stuff import Box
from template import Template


# これは何？日本語を書けますよ
# 英語を書けない？なんで？

class Game:
    def __init__(self, deck: Deck = None):

        self.build_direction: bool = True
        if deck is None: deck = Deck()
        self.deck: Deck = deck
        self.turn = 1
        self.select_index: int = 1
        self.card_index: int = 0

    def get_available_box(self) -> Box:
        available_box = Box()
        for card in self.deck.sorted_by_distance():
            if card.is_destroyed(): continue
            available_box += card.storage.to_flow()
        return available_box

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

    def calculate(self) -> None:
        print(f"\n - Turn {self.turn} - \n")
        self.turn += 1

        for card in self.deck.sorted_by_distance():
            card.reset_status()

        for priority in range(0, 10):
            for card in self.deck.sorted_by_distance():
                if card.is_destroyed(): continue
                if card.priority != priority: continue
                if self.get_available_box() < card.inflow: continue
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

    def can_buy(self, price: Box) -> bool:
        return not self.get_available_box() < price

    def buy(self, card: Card) -> None:
        if not self.can_buy(card.stats().price):
            raise Exception(f"Can't buy {card.name} for {card.stats().price}")
        self.collect_purchase_from_other_cards(card)
        self.deck.add_card(card, is_below=self.build_direction)
        if not self.build_direction:
            self.card_index += 1

    def sell(self, index: int) -> None:
        card = self.deck.cards[index]
        sell_price: Box = card.purchased * 0.75
        print(f"SELL: {card.name} >> {sell_price}")
        card.storage += sell_price
        self.store_to_other_cards(card)
        for other in self.deck.sorted_by_distance(card):
            if not other == card:
                self.select_index = self.deck.cards.index(other)
        del self.deck.cards[index]

    def can_upgrade(self, index: int) -> bool:
        card = self.deck.cards[index]
        if card.level == len(card.levels):
            print(f"UPGRADE: {card.name} is at its max level")
            return False
        if not card.next_stats().unlocked:
            print(f"UPGRADE: {card.name} has not unlocked level {card.level + 1}")
            return False
        return not self.get_available_box() < card.next_stats().price

    def upgrade(self, index: int) -> None:
        card = self.deck.cards[index]
        if not self.can_upgrade(index):
            raise Exception(f"Can't upgrade {card.name}!")
        card_value = card.purchased.to_flow()
        card.purchased = Box()
        card.level_up()
        self.collect_purchase_from_other_cards(card)
        card.purchased += card_value

    def research(self, card: Card) -> None:
        for level in card.levels:
            if not level.unlocked:
                if self.get_available_box() < level.research_cost:
                    print(f"RESEARCH: Not enough resources to research {card.name} level {level.level}")
                    return
                levelled_card = copy.deepcopy(card)
                levelled_card.level = level.level
                self.collect_research_from_other_cards(levelled_card)
                level.unlocked = True
                print(f"RESEARCH: Unlocked level {level.level} for {card.name}")
                return
        print(f"RESEARCH: {card.name} has been fully researched")

    def swap(self, i: int, j: int) -> None:
        temp: Card = self.deck.cards[i]
        self.deck.cards[i] = self.deck.cards[j]
        self.deck.cards[j] = temp
        print(f"SWAP: {self.deck.cards[j].name} <-> {self.deck.cards[i].name}")

    def change_card_index(self, amount: int) -> None:
        self.card_index += amount
        if self.card_index not in range(len(self.deck.cards)):
            print(f"FOCUS: {self.card_index} is invalid")
            self.card_index -= amount
        print(f"FOCUS: {self.card_index}")

    def change_select_index(self, amount: int) -> None:
        original_index = self.select_index
        while True:
            self.select_index += amount
            if self.select_index not in range(len(Template)):
                print(f"SELECT: {self.select_index} is out of bounds")
                self.select_index = original_index
                break
            if list(Template)[self.select_index].value.is_interactable:
                break
            print(f"SELECT: {self.select_index} ({list(Template)[self.select_index].value.name}) is not interactable")
        print(f"SELECT: {self.select_index} ({list(Template)[self.select_index].value.name})")

    def selected_card(self) -> Card:
        return copy.deepcopy(list(Template)[self.select_index].value)

    def set_build_direction(self, direction: bool) -> None:
        self.build_direction = direction
        print(f"BUILD_UP: {self.build_direction}")


class Shop:
    def __init__(self) -> None:
        self.inventory: list[Card] = []
        for card in Template:
            if not card.value.is_interactable: continue
            self.inventory.append(card.value)
