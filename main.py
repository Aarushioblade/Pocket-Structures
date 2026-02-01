from structures import Deck, Blueprints
from calculator import Game
from stuff import Box, Flow


def main():
    deck = Deck()
    game = Game(deck)
    deck += Blueprints.CORE
    for i in range(2): deck += Blueprints.GENERATOR
    deck += Blueprints.SHIELD
    deck.sorted_by_distance(deck[1])
    while True:
        for i in range(1): game.calculate()
        print(deck)
        input("Press any key to continue...")


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