from enum import Enum

from card import Card, Level
from stuff import Box, Flow


class Template(Enum):

    CORE = Card("Core", Box(health=360, starbit=120), [
        Level(1, Box(health=360, material=12, energy=72, starbit=15000, shield=120, boost=0),
              Flow(energy=+6), price=Box(), unlocked=True, effect_range=0, effect_flow=Flow(health=+2)),
        Level(2, Box(health=720, material=36, energy=144, starbit=15000, shield=360, boost=0),
              Flow(energy=+24), price=Box(energy=240, material=132, starbit=300), unlocked=True, effect_range=2,
              effect_flow=Flow(health=+12)),
        Level(3, Box(health=1200, material=96, energy=240, starbit=15000, shield=800),
              Flow(energy=+36), price=Box(energy=600, material=480, starbit=732), unlocked=True, effect_range=4,
              effect_flow=Flow(health=+24, boost=+75)),
    ], priority=0, is_interactable=False, is_core=True)

    MINE = Card("Laser Mine", Box(health=72), [
        Level(1, Box(health=72, shield=72), Flow(material=+3, energy=-8), Box(starbit=18), False,
              research_cost=Box(energy=36)),
        Level(2, Box(health=78, shield=78), Flow(material=+12, energy=-20), Box(starbit=24), False,
              research_cost=Box(starbit=96)),
        Level(3, Box(health=84, shield=84), Flow(material=+64, energy=-32), Box(starbit=30), False,
              research_cost=Box(starbit=180)),
    ], 2)

    FACTORY = Card("Factory", Box(health=72), [
        Level(1, Box(health=72, shield=72), Flow(material=-9, energy=-6, starbit=+7), Box(starbit=24), False,
              research_cost=Box(material=1)),
        Level(2, Box(health=78, shield=78), Flow(material=-24, energy=-15, starbit=+16), Box(starbit=30), False,
              research_cost=Box(starbit=180)),
        Level(3, Box(health=84, shield=84), Flow(material=-72, energy=-45, starbit=+60), Box(starbit=36), False,
              research_cost=Box(starbit=360)),
    ], 3)

    CANNON = Card("Star Cannon", Box(health=132), [
        Level(1, Box(health=132, shield=132), Flow(energy=-6, material=-3), Box(starbit=24), False, 1, Flow(health=-3),
              research_cost=Box(starbit=8)),
        Level(2, Box(health=138, shield=138), Flow(energy=-12, material=-6), Box(starbit=36), False, 2,
              Flow(health=-12),
              research_cost=Box(starbit=72)),
        Level(3, Box(health=144, shield=144), Flow(energy=-24, material=-12), Box(starbit=48), False, 3,
              Flow(health=-36),
              research_cost=Box(starbit=216)),
    ], 5, requires_enemies=True)

    GENERATOR = Card("Generator", Box(health=36), [
        Level(1, Box(health=36, shield=36), Flow(energy=+12), Box(starbit=12), True),
        Level(2, Box(health=42, shield=42), Flow(energy=+36), Box(starbit=16), False,
              research_cost=Box(starbit=15), precondition=[(FACTORY, 1)]),
        Level(3, Box(health=48, shield=48), Flow(energy=+72), Box(starbit=20), False,
              research_cost=Box(starbit=72)),
        Level(4, Box(health=54, shield=54), Flow(energy=+144), Box(starbit=24), False,
              research_cost=Box(starbit=100)),
        Level(5, Box(health=60, shield=60), Flow(energy=+360), Box(starbit=24), False,
              research_cost=Box(starbit=100)),
    ], 1)

    STORAGE = Card("Storage", Box(health=120), [
        Level(1, Box(health=120, material=36, shield=120), Flow(), Box(starbit=12), False,
              research_cost=Box(material=10), precondition=[(FACTORY, 1)]),
        Level(2, Box(health=126, material=120, shield=126), Flow(), Box(starbit=16), False,
              research_cost=Box(starbit=32)),
        Level(3, Box(health=132, material=252, shield=132), Flow(), Box(starbit=84), False,
              research_cost=Box(starbit=120)),
    ], 4)

    POWER_BOX = Card("Power Box", Box(health=120), [
        Level(1, Box(health=120, energy=84, shield=120), Flow(), Box(starbit=12), False,
              research_cost=Box(energy=15), precondition=[(FACTORY, 1)]),
        Level(2, Box(health=126, energy=216, shield=126), Flow(), Box(starbit=16), False,
              research_cost=Box(starbit=32)),
        Level(3, Box(health=132, energy=456, shield=132), Flow(), Box(starbit=84), False,
              research_cost=Box(starbit=120)),
    ], 4)

    HYPERBEAM = Card("Hyperbeam", Box(health=156), [
        Level(1, Box(health=156, shield=156), Flow(energy=-60), Box(starbit=200), False, 2, Flow(health=-20),
              research_cost=Box(starbit=276), precondition=[(CANNON, 1), (POWER_BOX, 1)]),
    ], 5, requires_enemies=True)

    ENEMY = Card("Enemy", Box(health=24), [
        Level(1, Box(health=24, shield=24), Flow(), Box(starbit=48), True, 1, effect_flow=Flow(health=-6)),
        Level(2, Box(health=60, shield=60), Flow(), Box(starbit=108), True, 1, effect_flow=Flow(health=-12)),
        Level(3, Box(health=120, shield=120), Flow(), Box(starbit=192), True, 1, effect_flow=Flow(health=-24)),
    ], 9, is_enemy=True, is_interactable=False)

    REGENERATOR = Card("Regenerator", Box(health=120), [
        Level(1, Box(health=120, shield=120), Flow(material=-12), Box(starbit=264), False, 3, Flow(health=+12),
              research_cost=Box(starbit=372), precondition=[(FACTORY, 1), (STORAGE, 1)]),
        Level(2, Box(health=126, shield=120), Flow(material=-36), Box(starbit=312), False, 4, Flow(health=+36),
              research_cost=Box(starbit=452)),
        Level(3, Box(health=132, shield=120), Flow(material=-72), Box(starbit=408), False, 5, Flow(health=+72),
              research_cost=Box(starbit=452))
    ], 6)

    SHIELD = Card("Shield", Box(health=24), [
        Level(1, Box(health=24, shield=276), Flow(energy=-24), Box(starbit=348), False, 2, Flow(shield=+6),
              research_cost=Box(starbit=564), precondition=[(REGENERATOR, 1)]),
        Level(2, Box(health=30, shield=282), Flow(energy=-48), Box(starbit=444), False, 3, Flow(shield=+12),
              research_cost=Box(starbit=612)),
        Level(3, Box(health=36, shield=288), Flow(energy=-84), Box(starbit=528), False, 4, Flow(shield=+36),
              research_cost=Box(starbit=744)),
    ], 7)

    BOOST = Card("Booster", Box(health=48), [
        Level(1, Box(health=48, shield=48), Flow(energy=-48, material=-2), Box(starbit=456), False, 1, Flow(boost=+50),
              research_cost=Box(starbit=852), precondition=[(SHIELD, 1)]),
        Level(2, Box(health=54, shield=54), Flow(energy=-60, material=-4), Box(starbit=516), False, 1, Flow(boost=+100),
              research_cost=Box(starbit=1284)),
        Level(3, Box(health=60, shield=60), Flow(energy=-96, material=-8), Box(starbit=636), False, 2, Flow(boost=+150),
              research_cost=Box(starbit=1476)),
    ], 8)

    FINALE = Card("Ultimate Megastructure", Box(health=1728), [
        Level(1, Box(health=1728, material=1728, energy=1728, shield=1728),
              Flow(energy=+1728, material=+1728, boost=+1728, shield=+1728, starbit=+1728), Box(starbit=15000), False,
              12, Flow(health=+1728), Box(starbit=15000), precondition=[(BOOST, 1)])
    ], 0)
