from deck import Deck
from calculator import Game
from stuff import Box, Flow
from template import Template


def main():
    print()
    deck = Deck()
    game = Game(deck)
    deck.add_card(Template.CORE.value)
    game.buy(Template.GENERATOR.value)
    game.research(Template.GENERATOR.value)
    game.upgrade(1)
    game.research(Template.GENERATOR.value)
    game.upgrade(1)
    game.research(Template.GENERATOR.value)
    game.buy(Template.FACTORY.value)
    game.buy(Template.MINE.value)
    game.swap(2, 3)
    game.research(Template.MINE.value)
    game.upgrade(2)
    game.calculate()
    game.sell(3)
    game.sell(2)
    game.sell(1)
    print(deck)


def stuff_calc():
    print(" - Stuff Calculator - \n")

    box = Box(9, 3, 5, 3, 5, 1)
    flow = Flow(1, 2, 4, 6, 4, 2)
    print(f"  {box}\n+ {flow.to_box()}\n= {box + flow}\n")
    print(f"  {box}\n- {flow.to_box()}\n= {box - flow}\n")
    print(f"  {box.to_flow()}\n% {flow}\n= {box % flow}\n")
    print(f"")


# deck*Template.BOOST + deck*Template.CORE == deck*(Template.BOOST + Template.CORE)

if __name__ == '__main__':
    main()