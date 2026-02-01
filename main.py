from structures import Deck, Blueprints
from calculator import Game
from stuff import Box, Flow


def main():
    deck = Deck()
    game = Game(deck)
    deck += Blueprints.CORE
    game.buy(Blueprints.GENERATOR)
    game.research(Blueprints.GENERATOR)
    game.upgrade(1)
    game.swap(0, 1)
    game.research(Blueprints.GENERATOR)
    game.research(Blueprints.GENERATOR)
    game.calculate()
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