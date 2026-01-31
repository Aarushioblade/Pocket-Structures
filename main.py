from structures import Deck, Blueprints
from calculator import Game
from stuff import Box, Flow


def main():
    deck = Deck()
    game = Game(deck)
    # deck += Blueprints.CORE
    deck += Blueprints.CORE
    # deck += Blueprints.SHIELD
    for i in range(3):
        deck += Blueprints.GENERATOR
        deck.cards[-1].level_up()
    deck += Blueprints.REGENERATOR
    deck += Blueprints.BOOST
    deck += Blueprints.FACTORY
    deck += Blueprints.MINE
    deck += Blueprints.BOOST
    deck += Blueprints.SHIELD
    # deck += Blueprints.SHIELD
    deck += Blueprints.ENEMY
    deck += Blueprints.ENEMY
    # deck[2].level_up()
    deck.sorted_by_distance(deck[1])
    for i in range(1): game.calculate()
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