from structures import Deck, Card, Blueprints
from stuff import Box


class Game:
    def __init__(self, deck: Deck):
        self.deck: Deck = deck
        self.turn = 1

    def get_available_box(self) -> Box:
        available_box = Box()
        for card in self.deck.sorted_by_distance(Blueprints.ENEMY):
            available_box += card.storage.to_flow()
        return available_box

    def store_to_other_cards(self, card: Card) -> None:
        for other in self.deck.sorted_by_distance(card):
            if other == card: continue
            card.store(other)

    def collect_from_other_cards(self, card: Card) -> None:
        for other in self.deck.sorted_by_distance(card):
            card.collect(other)

    def calculate(self) -> None:
        print(f"\n - Turn {self.turn} - \n")
        self.turn += 1

        for priority in range(0, 10):
            for card in self.deck.sorted_by_distance(Blueprints.ENEMY):
                if card.priority != priority: continue
                if self.get_available_box() < card.inflow: continue
                self.collect_from_other_cards(card)
                card.produce()
                self.store_to_other_cards(card)

        for card in self.deck.sorted_by_distance(Blueprints.ENEMY):
            self.store_to_other_cards(card)
            card.reset()
