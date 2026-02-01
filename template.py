from enum import Enum

from card import Card, Level
from stuff import Box, Flow


class Template(Enum):
    CORE = Card("Core", Box(health=1000, starbit=1000), [
        Level(1, Box(health=1000, material=30, energy=60, starbit=15000, shield=200, boost=0),
              Flow(energy=+6), price=Box(), unlocked=True, effect_range=1, effect_flow=Flow(health=+5))
    ], priority=0, is_interactable=False, is_core=True)
    GENERATOR = Card("Generator", Box(health=100), [
        Level(1, Box(health=100, shield=100), Flow(energy=12), Box(starbit=60), True),
        Level(2, Box(health=135), Flow(energy=36), Box(starbit=120), False),
        Level(3, Box(health=180), Flow(energy=72), Box(starbit=180), False),
    ], 1)
    MINE = Card("Laser Mine", Box(health=100), [
        Level(1, Box(health=100), Flow(material=+6, energy=-8), Box(starbit=80), True),
        Level(2, Box(health=120), Flow(material=+18, energy=-14), Box(starbit=160), False),
        Level(3, Box(health=140), Flow(material=+64, energy=-32), Box(starbit=340), False),
    ], 2)
    FACTORY = Card("Factory", Box(health=100), [
        Level(1, Box(health=100), Flow(material=-6, energy=-3, starbit=+24), Box(starbit=100), True),
    ], 3)
    STORAGE = Card("Storage", Box(health=120), [
        Level(1, Box(health=120, material=60), Flow(), Box(starbit=150), True),
    ], 4)
    POWER_BOX = Card("Power Box", Box(health=120), [
        Level(1, Box(health=120, energy=80), Flow(), Box(starbit=150), True),
    ], 4)
    # not required to work
    HYPERBEAM = Card("Hyperbeam", Box(health=120), [
        Level(1, Box(health=120), Flow(energy=-20), Box(starbit=200), True, 2, Flow(health=-20)),
    ], 5)
    ENEMY = Card("Enemy", Box(health=60), [
        Level(1, Box(health=60), Flow(), Box(), True, 1, effect_flow=Flow(health=-15)),
    ], 9, is_enemy=True, is_interactable=False)
    BOOST = Card("Boost", Box(health=48), [
        Level(1, Box(health=48), Flow(energy=-20, material=-5), Box(starbit=400), True, 1, Flow(boost=+50)),
    ], 8)
    REGENERATOR = Card("Regenerator", Box(health=100), [
        Level(1, Box(health=100), Flow(energy=-2, material=-8), Box(starbit=250), True, 3, Flow(health=+10)),
    ], 6)
    SHIELD = Card("Shield", Box(health=64), [
        Level(1, Box(health=64, shield=150), Flow(energy=-20), Box(starbit=500), True, 2, Flow(shield=+50)),
    ], 7)
    # don't expect these to work
    DIMENSION = Card("Pocket Dimension", Box(health=0), [
        Level(1, Box(health=0), Flow(energy=-100), Box(starbit=900), True),
    ], 8)
    PARALLEL = Card("Parallel Stacker", Box(health=0), [
        Level(1, Box(health=0), Flow(energy=-110), Box(starbit=1000), True),
    ], 8)
    DESTROYER = Card("Destroyer Base", Box(health=200), [
        Level(1, Box(health=200), Flow(health=-30, energy=-50), Box(starbit=1200), True),
    ], 6)


if __name__ == '__main__':

    for card in Template:
        if not card.value.is_interactable:
            print("NOT INTERACTABLE")
        print(card.value)
