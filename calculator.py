from structures import Deck
from stuff import Box


class Game:
    def __init__(self, deck: Deck):
        self.deck: Deck = deck
        self.turn = 1

    def get_available_box(self) -> Box:
        available_box = Box()
        for card in self.deck:
            available_box += card.storage.to_flow()
        return available_box

    def calculate(self) -> None:
        print(f"\n - Turn {self.turn} - \n")
        self.turn += 1

        for priority in range(0, 10):
            for card in self.deck:
                if card.priority != priority: continue
                if self.get_available_box() < card.inflow: continue
                for other in self.deck:
                    card.collect(other)
                card.produce()
                for other in self.deck:
                    if other == card: continue
                    card.store(other)

        for card in self.deck:
            card.reset()
