from structures import Deck
from calculator import Game
from stuff import Box, Flow
from blueprints import Blueprints


def main():
    deck = Deck()
    game = Game(deck)
    deck += Blueprints.CORE
    game.buy(Blueprints.GENERATOR)
    game.research(Blueprints.GENERATOR)
    game.upgrade(1)
    game.research(Blueprints.GENERATOR)
    game.upgrade(1)
    game.research(Blueprints.GENERATOR)
    game.buy(Blueprints.FACTORY)
    game.buy(Blueprints.MINE)
    game.swap(2, 3)
    game.research(Blueprints.MINE)
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



# deck*Blueprints.BOOST + deck*Blueprints.CORE == deck*(Blueprints.BOOST + Blueprints.CORE)

if __name__ == '__main__':
    main()