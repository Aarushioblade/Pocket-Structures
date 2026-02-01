from structures import Deck, Card
from stuff import Box


# これは何？日本語を書けますよ
# 英語を書けない？なんで？

class Game:
    def __init__(self, deck: Deck):
        self.deck: Deck = deck
        self.turn = 1

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
            card.reset_status_effects()

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
        self.deck += card
