from enum import Enum

from card import Card, Level
from stuff import Box, Flow


class Template(Enum):
    CORE = Card("Core", Box(health=360, starbit=72000), [
        Level(1, Box(health=360, material=12, energy=72, starbit=15000, shield=120, boost=0),
              Flow(energy=+6), price=Box(), unlocked=True, effect_range=0, effect_flow=Flow(health=+2)),
        Level(2, Box(health=720, material=36, energy=144, starbit=15000, shield=360, boost=0),
              Flow(energy=+24, ), price=Box(), unlocked=False, effect_range=0, effect_flow=Flow(health=+6),
              research_cost=Box(energy=240, material=132, starbit=300)),
    ], priority=0, is_interactable=False, is_core=True)
    GENERATOR = Card("Generator", Box(health=36), [
        Level(1, Box(health=36, shield=36), Flow(energy=+12), Box(starbit=12), True),
        Level(2, Box(health=42, shield=42), Flow(energy=+36), Box(starbit=16), False,
              research_cost=Box(starbit=15)),
        Level(3, Box(health=48), Flow(energy=+72), Box(starbit=20), False,
              research_cost=Box(starbit=72)),
        Level(4, Box(health=54), Flow(energy=+144), Box(starbit=24), False,
              research_cost=Box(starbit=100)),
        Level(5, Box(health=60), Flow(energy=+360), Box(starbit=24), False,
              research_cost=Box(starbit=100)),
    ], 1)
    MINE = Card("Laser Mine", Box(health=72), [
        Level(1, Box(health=72), Flow(material=+3, energy=-8), Box(starbit=18), False,
              research_cost=Box(energy=36)),
        Level(2, Box(health=78), Flow(material=+12, energy=-20), Box(starbit=24), False,
              research_cost=Box(starbit=96)),
        Level(3, Box(health=84), Flow(material=+64, energy=-32), Box(starbit=30), False,
              research_cost=Box(starbit=180)),
    ], 2)
    FACTORY = Card("Factory", Box(health=72), [
        Level(1, Box(health=72), Flow(material=-9, energy=-6, starbit=+4), Box(starbit=24), False,
              research_cost=Box(material=6)),
        Level(2, Box(health=78), Flow(material=-24, energy=-15, starbit=+12), Box(starbit=30), False,
              research_cost=Box(starbit=180)),
        Level(3, Box(health=84), Flow(material=-72, energy=-45, starbit=+60), Box(starbit=36), False,
              research_cost=Box(starbit=360)),
    ], 3)
    STORAGE = Card("Storage", Box(health=120), [
        Level(1, Box(health=120, material=36), Flow(), Box(starbit=12), False,
              research_cost=Box(material=10)),
        Level(2, Box(health=126, material=120), Flow(), Box(starbit=16), False,
              research_cost=Box(starbit=32)),
        Level(3, Box(health=132, material=252), Flow(), Box(starbit=84), False,
              research_cost=Box(starbit=120)),
    ], 4)
    POWER_BOX = Card("Power Box", Box(health=120), [
        Level(1, Box(health=120, energy=84), Flow(), Box(starbit=12), False,
              research_cost=Box(energy=15)),
        Level(2, Box(health=126, energy=216), Flow(), Box(starbit=16), False,
              research_cost=Box(starbit=32)),
        Level(3, Box(health=132, energy=456), Flow(), Box(starbit=84), False,
              research_cost=Box(starbit=120)),
    ], 4)
    # not required to work
    CANNON = Card("Star Cannon", Box(health=132), [
        Level(1, Box(health=132), Flow(energy=-6, material=-3), Box(starbit=24), False, 1, Flow(health=-3),
              research_cost=Box(starbit=8)),
        Level(2, Box(health=138), Flow(energy=-12, material=-6), Box(starbit=36), False, 1, Flow(health=-12),
              research_cost=Box(starbit=72)),
        Level(3, Box(health=144), Flow(energy=-24, material=-12), Box(starbit=48), False, 1, Flow(health=-36),
              research_cost=Box(starbit=216)),
    ], 5, requires_enemies=True)
    HYPERBEAM = Card("Hyperbeam", Box(health=156), [
        Level(1, Box(health=156), Flow(energy=-60), Box(starbit=200), False, 2, Flow(health=-20),
              research_cost=Box(starbit=276)),
    ], 5, requires_enemies=True)
    ENEMY = Card("Enemy", Box(health=24), [
        Level(1, Box(health=24), Flow(), Box(starbit=48), True, 1, effect_flow=Flow(health=-6)),
        Level(2, Box(health=60), Flow(), Box(starbit=108), True, 1, effect_flow=Flow(health=-12)),
        Level(3, Box(health=120), Flow(), Box(starbit=192), True, 1, effect_flow=Flow(health=-24)),
    ], 9, is_enemy=True, is_interactable=False)
    BOOST = Card("Booster", Box(health=48), [
        Level(1, Box(health=48), Flow(energy=-48, material=-2), Box(starbit=456), False, 1, Flow(boost=+50),
              research_cost=Box(starbit=852)),
    ], 8)
    REGENERATOR = Card("Regenerator", Box(health=100), [
        Level(1, Box(health=120), Flow(material=-10), Box(starbit=264), False, 3, Flow(health=+10),
              research_cost=Box(starbit=372)),
    ], 6)
    SHIELD = Card("Shield", Box(health=64), [
        Level(1, Box(health=24, shield=276), Flow(energy=-20), Box(starbit=348), False, 2, Flow(shield=+6),
              research_cost=Box(starbit=564)),
    ], 7)
    FINALE = Card("ULTIMATE MEGASTRUCTURE", Box(health=1728), [
        Level(1, Box(health=1000, material=1728, energy=1728, shield=1728, starbit=15000),
              Flow(energy=+564, material=+732, boost=+12, shield=+12, starbit=+250), Box(starbit=15000), False, 12,
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
