from enum import Enum

from card import Card, Level
from stuff import Box, Flow


class Template(Enum):
    CORE = Card("Core", Box(health=500, starbit=100), [
        Level(1, Box(health=500, material=10, energy=15, starbit=15000, shield=200, boost=0),
              Flow(energy=+1), price=Box(), unlocked=True, effect_range=0, effect_flow=Flow(health=+1))
    ], priority=0, is_interactable=False, is_core=True)
    GENERATOR = Card("Generator", Box(health=30), [
        Level(1, Box(health=30, shield=100), Flow(energy=+2), Box(starbit=10), True),
        Level(2, Box(health=35, shield=100), Flow(energy=+5), Box(starbit=5), False,
              research_cost=Box(energy=15)),
        Level(3, Box(health=40), Flow(energy=36), Box(starbit=120), False,
              research_cost=Box(energy=20)),
        Level(4, Box(health=45), Flow(energy=72), Box(starbit=180), False,
              research_cost=Box(starbit=100)),
    ], 1)
    MINE = Card("Laser Mine", Box(health=100), [
        Level(1, Box(health=100), Flow(material=+2, energy=-4), Box(starbit=15), False,
              research_cost=Box(energy=10)),
        Level(2, Box(health=105), Flow(material=+12, energy=-20), Box(starbit=10), False,
              research_cost=Box(energy=20)),
        Level(3, Box(health=110), Flow(material=+64, energy=-32), Box(starbit=20), False,
              research_cost=Box(starbit=100)),
    ], 2)
    FACTORY = Card("Factory", Box(health=100), [
        Level(1, Box(health=100), Flow(material=-6, energy=-3, starbit=+4), Box(starbit=20), False,
              research_cost=Box(material=5)),
        Level(2, Box(health=105), Flow(material=-20, energy=-15, starbit=+12), Box(starbit=15), False,
              research_cost=Box(material=10)),
        Level(3, Box(health=110), Flow(material=-80, energy=-45, starbit=+60), Box(starbit=30), False,
              research_cost=Box(starbit=100)),
    ], 3)
    STORAGE = Card("Storage", Box(health=120), [
        Level(1, Box(health=110, material=10), Flow(), Box(starbit=5), False,
              research_cost=Box(material=10)),
    ], 4)
    POWER_BOX = Card("Power Box", Box(health=120), [
        Level(1, Box(health=110, energy=10), Flow(), Box(starbit=5), False,
              research_cost=Box(energy=15)),
    ], 4)
    # not required to work
    CANNON = Card("Star Cannon", Box(health=110), [
        Level(1, Box(health=110), Flow(energy=-1, material=-2), Box(starbit=20), False, 1, Flow(health=-2),
              research_cost=Box(starbit=5))
    ], 5, requires_enemies=True)
    HYPERBEAM = Card("Hyperbeam", Box(health=120), [
        Level(1, Box(health=120), Flow(energy=-20), Box(starbit=200), False, 2, Flow(health=-20)),
    ], 5, requires_enemies=True)
    ENEMY = Card("Enemy", Box(health=10), [
        Level(1, Box(health=20), Flow(), Box(starbit=50), True, 1, effect_flow=Flow(health=-5)),
    ], 9, is_enemy=True, is_interactable=False)
    BOOST = Card("Booster", Box(health=48), [
        Level(1, Box(health=48), Flow(energy=-20, material=-5), Box(starbit=400), False, 1, Flow(boost=+50),
              research_cost=Box(starbit=900)),
    ], 8)
    REGENERATOR = Card("Regenerator", Box(health=100), [
        Level(1, Box(health=100), Flow(material=-10), Box(starbit=250), False, 3, Flow(health=+10)),
    ], 6)
    SHIELD = Card("Shield", Box(health=64), [
        Level(1, Box(health=64, shield=150), Flow(energy=-20), Box(starbit=500), False, 2, Flow(shield=+50),
              research_cost=Box(starbit=650)),
    ], 7)
    FINALE = Card("ULTIMATE MEGASTRUCTURE", Box(health=1000, material=500, energy=500), [
        Level(1, Box(health=1000, material=500, energy=500, shield=500, starbit=15000),
              Flow(energy=+50, material=+50, boost=+10, shield=+10, starbit=+250), Box(starbit=15000), False, 8,
              Flow(health=+25), Box(starbit=15000))
    ], 0)
    NULL = Card("Empty", Box(health=64), [Level(1, Box(), Flow(), Box())], -1, is_interactable=False)
    # don't expect these to work
    DIMENSION = Card("Pocket Dimension", Box(health=0), [
        Level(1, Box(health=0), Flow(energy=-100), Box(starbit=900), False, research_cost=Box(starbit=1400)),
    ], 8, is_interactable=False)
    PARALLEL = Card("Parallel Stacker", Box(health=0), [
        Level(1, Box(health=0), Flow(energy=-110), Box(starbit=1000), False),
    ], 8, is_interactable=False)
    DESTROYER = Card("Destroyer Base", Box(health=200), [
        Level(1, Box(health=200), Flow(health=-30, energy=-50), Box(starbit=1200), False),
    ], 6, is_interactable=False)


if __name__ == '__main__':

    for card in Template:
        if not card.value.is_interactable:
            print("NOT INTERACTABLE")
        print(card.value)
