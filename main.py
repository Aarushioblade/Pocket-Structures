from structures import Deck, Blueprints
from calculator import Game
from stuff import Box, Flow


def main():
    deck = Deck()
    game = Game(deck)
    # deck += Blueprints.CORE
    deck += Blueprints.POWER_BOX
    deck += Blueprints.ENEMY
    deck += Blueprints.GENERATOR
    deck += Blueprints.POWER_BOX
    for card in deck:
        print(card)
    for i in range(6): game.calculate()
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