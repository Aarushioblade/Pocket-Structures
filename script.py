# This is a sample Python script.
import math
import time
import colorama
from colorama import Fore as txt
colorama.init()
# import random
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
reset = txt.RESET
blue = txt.LIGHTBLUE_EX
green = txt.LIGHTGREEN_EX
red = txt.LIGHTRED_EX
magenta = txt.LIGHTMAGENTA_EX
yellow = txt.LIGHTYELLOW_EX

CORE_SAFETY = True
HIDDEN_STATS = False
CONTINUE = False
start_time = time.time()
def print_hi():
    # Use a breakpoint in the code line below to debug your script.
    print(f'Welcome to {magenta}{colorama.Style.BRIGHT}Pocket Structures!{reset}{colorama.Style.RESET_ALL}')  # Press Ctrl+F8 to toggle the breakpoint.
    print(f"In this game, your goal is to manage structure production flows to generate as many starbits as possible")
    print(f"through building, destroying, upgrading, researching, and moving structures!")
    print(f"The only structure you cannot manipulate is known as the {magenta}Core{reset}, your starter structure.")
    print(f"Make sure to defend it well. If your core is destroyed, all is lost. ")
    print(f"In order to win, your core must contain at least {magenta}15,000{reset} starbits.")
    print(f"Good luck, Pocket Builder!\n\n\n")
    input("Press Enter to continue...")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
class XY:
    def __init__(self,x=0,y=0):
        self.x = x
        self.y = y
    def __str__(self):
        return f'({self.x},{self.y})'
    def set(self,x,y):
        self.x = x
        self.y = y
    def get_x(self):
        return self.x
    def get_y(self):
        return self.y
    def distance(self,other):
        return math.dist([self.x,self.y],[other.get_x(),other.get_y()])

class Card:
    no_override = ["Energy","Material","Health","Storage","Max Level"]
    def __init__(self,name="Card"):
        self.name = name
        self.stats = {"Level":1,"Max Level":1}
        self.upgrade = None
        self.idx = -1
        self.xy = XY()
    def move(self,x,y):
        self.xy.set(x,y)
    def get_xy(self):
        return self.xy
    def set_name(self,name):
        self.name = name
    def get_name(self,bg=reset):
        p = f"[{self.idx}] " if self.idx >= 0 else ""
        if self.stat("Level") > 1:
            s = f" [{magenta if bg==reset else bg}LVL{self.stat('Level')}{bg}]"
        else: s = ""
        return p + self.name + s
    def __str__(self):
        s = self.get_name()
        #s += str(self.stats)
        for key,v in zip(self.stats.keys(),self.stats.values()):
            #s += f"\n-\t{key}: {f'{value}':<15}"
            if key in ["Level","Active","Max Level","Range"]:
                if HIDDEN_STATS: continue
            #s += txt.RESET
            if v < 0: color = red
            elif "Energy" in key: color = blue
            elif "Material" in key: color = yellow
            elif "Health" in key: color = green
            elif "Starbit" in key: color = magenta
            else: color = reset
            value = f"{v:+}" if "Flow" in key else f"{v}"
            s += f"\n{color}|{reset}\t"
            s += "{0:<17}{1:>10}".format(key,color + value)
            s += txt.RESET
        return s
    def add_stat(self,stat,value):
        self.stats[stat] = value
    def copy(self):
        c = Card()
        c.name = self.name
        c.stats = self.stats.copy()
        if self.upgrade: c.upgrade = self.upgrade.copy()
        return c
    def get_stats(self):
        return self.stats
    def set_upgrade(self,card):
        self.upgrade = card.copy()
    def upgrade_now(self):

        if not self.upgrade:
            if self.stats['Level'] < self.stats['Max Level']:
                print(f"{red}Further research is required to upgrade {self.get_name(red)} to level {self.stats['Level'] + 1}{reset}")
            else: print(f"{magenta}{self.get_name(magenta)} has already been upgraded to its maximum level!{reset}")
            return
        # we have to override stats carefully
        #self.stats = self.upgrade.get_stats()
        print(f"Upgraded {self.get_name()} {magenta}->{reset} {self.upgrade.get_name()}")
        for key,value in zip(self.upgrade.get_stats().keys(),self.upgrade.get_stats().values()):
            # don't update the value
            if key in Card.no_override:
                if key in ["Max Level"] and HIDDEN_STATS: continue
                print(f"{magenta}|{reset}\t{key} remains at {self.stats[key]}")
                continue
            print(f"{magenta}|{reset}\tChanged {key} from {self.stats.get(key)} to {value}")
            self.stats[key] = value
        self.name = self.upgrade.name
        self.upgrade = self.upgrade.upgrade
    ## returns the value of the stat with a key, which may be 0 if nonexistent
    def stat(self,key):
        return self.stats.get(key,0)
    ## returns True if the card does not have an active stat
    def activated(self):
        return self.stats.get("Active",True)

class Deck:
    def __init__(self):
        self.name = "Pocket Factory"
        self.cards = []
        self.CORE = None
    def __str__(self):
        s = f"{self.name} contains {len(self.cards)} cards:"
        for i in range(len(self.cards)):
            s += f"\n{self.cards[i]}"
        return s
    def __repr__(self):
        return "Deck"
    def add_card(self, card,num = 1):
        for i in range(num):
            c = card.copy()
            c.idx = len(self.cards)
            if c.idx == 0: self.CORE = c
            self.cards.append(c)
    def get_card(self,idx) -> Card:
        if idx >= len(self.cards):
            return self.cards[0]
        return self.cards[idx]
    def upgrade_card(self,idx):
        self.cards[idx].upgrade_now()
    def filter(self,*args):
        new_arr = []
        for card in self.cards:
            if card.name in args:
                new_arr.append(card)
        return new_arr
    def cycle(self):
        p_energy = 0
        c_energy = 0
        for card in self.cards:
            f = card.get_stats()
            if f.get("Energy Flow",0) > 0: p_energy += f.get("Energy Flow",0)
            elif f.get("Energy Flow",0) < 0: c_energy -= f.get("Energy Flow",0)

        print()
        print(f"Energy production:  {blue}{p_energy}{reset}")
        print(f"Energy consumption: {red}{c_energy}{reset}")
        try:
            sufficiency = 100 * min(1.0,p_energy/c_energy)
        except ZeroDivisionError:
            sufficiency = 100
        color = magenta if sufficiency > 90 else blue if sufficiency > 80 else yellow if sufficiency > 50 else red
        print(f"Energy sufficiency: {color}{sufficiency:.1f}%{reset}")
        d_energy = 0 #p_energy - c_energy
        pc_energy = p_energy - c_energy
        u_energy = p_energy
        ## Energy calculations
        for card in self.cards:
            ## ignore cards generating energy
            if card.stat("Energy Flow") == 0: continue
            color = blue if card.stat('Energy Flow') > 0 else red
            print(f"{color}|{reset}\t" + "{0:<21}{1:>15}".format(f"{card.get_name()} ", f"{color}{card.stat('Energy Flow'):+}{reset}"))
            if card.stat("Energy Flow") >= 0: continue
            ## these are the cards that use energy and have enough of it
            if u_energy + card.stat("Energy Flow") >= 0:
                u_energy += card.stat("Energy Flow")
                #print("|\t"+"{0:<15}{1:>14}".format(f"{card.get_name()}",f"{blue}{card.stat('Energy Flow')}{reset}"))
                card.add_stat("Active",True)
                continue
            n_energy = abs(u_energy + card.stat("Energy Flow"))
            print(f"{card.get_name()} requires {blue}{n_energy}{reset} more energy to operate. Checking energy reserves..")
            stored_energy = 0
            for energy_card in self.filter("Core","Energy Storage"):
                s_energy = energy_card.stat("Energy")
                stored_energy += s_energy
            if stored_energy < n_energy:
                print(f"{red}|{reset}\tOnly found {blue}{stored_energy}{reset} energy in reserves")
                print(f"{red}|{reset}\t{blue}{n_energy - stored_energy}{reset} energy is still needed to power {card.get_name()}")
                card.add_stat("Active",False)
                continue
            # we now know there is enough energy to power the structure
            # therefore, we can extract that energy from both the potential and storage energies
            if u_energy > 0: print(f"{blue}|{reset}\tTransferred remaining {blue}{u_energy}{reset} potential energy to {card.get_name()}")
            u_energy += card.stat("Energy Flow") + n_energy
            for energy_card in self.filter("Core","Energy Storage"):
                s_energy = energy_card.stat("Energy")
                transfer = min(s_energy, n_energy)
                n_energy -= transfer
                d_energy -= transfer
                energy_card.add_stat("Energy",s_energy - transfer)
                print(f"{blue}|{reset}\tTransferred {blue}{transfer}{reset} energy from {energy_card.get_name()} to {card.get_name()}")
                print(f"{blue}|{reset}\t{energy_card.get_name()} now has {blue}{energy_card.stat('Energy')}{reset} energy remaining")
                if n_energy == 0: break
            if n_energy > 0:
                print(f"{red}Something went wrong..{reset}")
                continue

            print(f"{blue}|{reset}\t{card.get_name()} now has all {blue}{abs(card.stat("Energy Flow"))}{reset} required energy")
            card.add_stat("Active",True)
        print("{0:<1}{1:>13}".format("Remaining Potential Energy:",f"{blue}{u_energy}{reset}"))
        if u_energy > 0:
            print(f"Handling excess energy...")
            for card in self.filter("Core","Energy Storage"):
                s_energy = card.stat("Max Energy") - card.stat("Energy")
                transfer = min(s_energy, u_energy)
                u_energy -= transfer
                d_energy += transfer
                card.add_stat("Energy",card.stat("Energy") + transfer)
                print(f"{blue}|{reset}\t{card.get_name()} energy transfer: {blue}{transfer:+}{reset} ({blue}{card.stat('Energy')}{reset}/{blue}{card.stat('Max Energy')}{reset})")
        if u_energy > 0: print(f"Unstored Potential Energy: {blue}{u_energy}{reset}")

        p_material = 0
        c_material = 0
        for card in self.cards:
            if not card.activated(): continue
            if card.stat("Material Flow") > 0:
                p_material += card.stat("Material Flow")

        for card in self.cards:
            if not card.activated(): continue
            if card.stat("Material Flow") < 0:
                c_material -= card.stat("Material Flow")

        print(f"Material production:  {yellow}{p_material}{reset}")
        print(f"Material consumption: {red}{c_material}{reset}")
        #d_material = p_material - c_material
        d_material = 0
        pc_material = p_material - c_material
        u_material = p_material
        for card in self.cards:
            if not card.activated(): continue
            ## Disregard all cards producing material
            if card.stat("Material Flow") >= 0:
                #d_material += card.stat("Material Flow")
                continue
            ## Material-consuming cards that have enough material
            if u_material + card.stat("Material Flow") >= 0:
                u_material += card.stat("Material Flow")
                #d_material += card.stat("Material Flow")
                card.add_stat("Active",True)
                continue
            n_material = abs(u_material + card.stat("Material Flow"))
            print(f"{card.get_name()} requires {yellow}{n_material}{reset} more material. Checking storage...")
            stored_material = 0
            for material_card in self.filter("Core","Storage"):
                stored_material += material_card.stat("Material")
            if stored_material < n_material:
                print(f"{red}|{reset}\tFound only {yellow}{stored_material}{reset} material in storage")
                print(f"{red}|{reset}\t{card.get_name()} is still awaiting {yellow}{n_material - stored_material}{reset} material.")
                card.add_stat("Active",False)
                continue
            if u_material > 0: print(f"{yellow}|{reset}\tTransferred remaining {yellow}{u_material}{reset} material to {card.get_name()}")

            u_material += card.stat("Material Flow") + n_material
            for material_card in self.filter("Core","Storage"):
                s_material = material_card.stat("Material")
                transfer = min(s_material, n_material)
                material_card.add_stat("Material",s_material - transfer)
                if transfer == 0: continue # yeah, this won't do anything
                print(f"{yellow}|{reset}\tTransferred {yellow}{transfer}{reset} material from {material_card.get_name()} to {card.get_name()}")
                print(f"{yellow}|{reset}\t{material_card.get_name()} has {yellow}{material_card.stat('Material')}{reset} material remaining")
                n_material -= transfer
                d_material -= transfer
                if n_material == 0: break
            if n_material > 0:
                print(f"{red}Something went wrong..{reset}")
                continue
            print(f"{yellow}|{reset}\t{card.get_name()} now has all {yellow}{abs(card.stat("Material Flow"))}{reset} required material")
            card.add_stat("Active", True)
        if u_material > 0:
            print(f"Handling excess material...")
            for card in self.filter("Core","Storage"):
                s_material = card.stat("Max Material") - card.stat("Material")
                transfer = min(s_material, u_material)
                u_material -= transfer
                card.add_stat("Material",card.stat("Material") + transfer)
                print(f"{yellow}|{reset}\t{card.get_name()} stored {yellow}{transfer:+}{reset} material ({yellow}{card.stat("Material")}{reset}/{yellow}{card.stat("Max Material")}{reset})")
                if u_material == 0: break
        if not self.CORE: return
        print("Calculating stat increases..")
        d_health = 0
        for card in self.cards:
            if not card.activated(): continue
            if card.stat("Health Flow") > 0:
                d_health += card.stat("Health Flow")
                transfer = min(card.stat("Health Flow"),self.CORE.stat("Max Health") - self.CORE.stat("Health"))
                self.CORE.add_stat("Health",self.CORE.stat("Health") + transfer)
                if transfer > 0: print(f"{green}|{reset}\t{card.get_name()} regenerated {green}{transfer:+}{reset} health to {"itself" if card == self.CORE else self.CORE.get_name()}")
        d_starbits = 0
        for card in self.cards:
            if card.stat("Starbit Flow") > 0 and card.activated():
                transfer = card.stat("Starbit Flow")
                self.CORE.add_stat("Starbits",self.CORE.stat("Starbits") + transfer)
                d_starbits += transfer
                print(f"{magenta}|{reset}\t{card.get_name()} has earned {magenta}{transfer:+}{reset} starbits")
        e = f"Energy: {blue if pc_energy >= 0 else red}{pc_energy:+}{reset}"
        m = f"Material: {yellow if pc_material >= 0 else red}{pc_material:+}{reset}"
        h = f"Health: {green if d_health >= 0 else red}{d_health:+}{reset}"
        b = f"Starbits: {magenta}{d_starbits:+}{reset}"
        s = f"{e} | {m} | {h} | {b}"
        u_energy = 0
        m_energy = 0
        for card in self.filter("Core","Energy Storage"):
            u_energy += card.stat("Energy")
            m_energy += card.stat("Max Energy")
        u_material = 0
        m_material = 0
        for card in self.filter("Core","Storage"):
            u_material += card.stat("Material")
            m_material += card.stat("Max Material")
        u_health = self.CORE.stat("Health")
        m_health = self.CORE.stat("Max Health")
        u_starbits = self.CORE.stat("Starbits")
        #if u_starbits >= 1000:
        #    u_starbits /= 1000
        #    u_starbits = str(round(u_starbits,2)) + "K"
        u_e = f"{blue}{u_energy}/{m_energy}".center(len(e) - 5)
        u_m = f"{yellow}{u_material}/{m_material}".center(len(m) - 5)
        u_h = f"{green}{u_health}/{m_health}".center(len(h) - 5)
        u_b = f"{magenta}{u_starbits}/15K".center(len(b) - 5)
        u_s = f"{u_e}{reset} | {u_m}{reset} | {u_h}{reset} | {u_b}{reset}"
        a = len(s) - 8*5
        c = int(a/2)
        for i in range(c): print("-=",end="")
        print()
        print("SUMMARY".center(a))
        print(s)
        print(u_s)
        for i in range(c): print("=-", end="")
        print()
    def card(self,name):
        for card in self.cards:
            if card.name == name:
                return card
        return None
    def rem(self,idx):
        card = self.cards.pop(idx)
        ## Re-index all cards
        for idx in range(len(self.cards)):
            self.cards[idx].idx = idx
        return card
    def clear(self,reset_core=False):
        for i in range(1,len(self.cards)):
            self.cards.pop(1)
        if reset_core:
            self.cards.clear()
            self.add_card(core)
            self.CORE = self.cards[0]
        print("Reset the deck")
        print(deck)
    def last_card(self):
        return self.cards[-1]
    def add_starbits(self,starbits):
        self.CORE.add_stat("Starbits",self.CORE.stat("Starbits") + starbits)
    def card_count(self):
        return len(self.cards)
    def compact_list(self):
        for card in self.cards:
            print(card.get_name())

class Structure:
    max_health = 100
    def __init__(self):
        self.position = XY(0,0)
        self.health = 100
    @classmethod
    def formatted(cls,*args) -> str:
        s = "w"
        for i in args:
            s += str(i)
        return s
class Core(Structure):
    energy_flow = 10
    health_flow = 5
    max_energy = 500
    def __init__(self):
        super().__init__()
        self.starbits = 0
        self.energy = 10
class Generator(Structure):
    energy_flow = 12
class LaserDrill(Structure):
    energy_flow = -10
    material_flow = 5
class Factory(Structure):
    energy_flow = -5
    material_flow = -10
    starbit_flow = 10
class Hyperbeam(Structure):
    energy_flow = -16
    range = 30
    damage = 40
class Storage(Structure):
    max_material = 200
    def __init__(self):
        super().__init__()
        self.material = 0
class EnergyStorage(Structure):
    max_energy = 300
    def __init__(self):
        super().__init__()
        self.energy = 0
class Regenerator(Structure):
    energy_flow = -1
    health_flow = 20
    range = 60
class Booster(Structure):
    energy_flow = -7
    range = 10

deck = Deck()

'''core = Card()
generator = Card()
generator_2 = Card()
generator_3 = Card()
laser_drill = Card()
factory = Card()
factory_2 = Card()
factory_3 = Card()
hyperbeam = Card()
storage = Card()
energy_storage = Card()
regenerator = Card()
booster = Card()'''

# <editor-fold desc="Card Base Stats">
core = Card("Core") #[|||||||||]
core.add_stat("Energy Flow",10)
core.add_stat("Energy",0)
core.add_stat("Max Energy",50)
core.add_stat("Material",0)
core.add_stat("Max Material",50)
core.add_stat("Health Flow",5)
core.add_stat("Health",1000)
core.add_stat("Max Health",1000)
core.add_stat("Starbits",0)
laser_drill = Card("Laser Drill")
laser_drill.add_stat("Max Level",3)
laser_drill.add_stat("Energy Flow",-10)
laser_drill.add_stat("Material Flow",6)
laser_drill.add_stat("Health",100)
laser_drill_2 = Card("Laser Drill")
laser_drill_2.add_stat("Level",2)
laser_drill_2.add_stat("Energy Flow",-35)
laser_drill_2.add_stat("Material Flow",24)
laser_drill_2.add_stat("Health",100)
laser_drill_3 = Card("Laser Drill")
laser_drill_3.add_stat("Level",3)
laser_drill_3.add_stat("Energy Flow",-72)
laser_drill_3.add_stat("Material Flow",68)
laser_drill_3.add_stat("Health",100)
storage = Card("Storage")
storage.add_stat("Max Level",2)
storage.add_stat("Material",0)
storage.add_stat("Max Material",500)
storage.add_stat("Health",100)
storage_2 = Card("Storage")
storage_2.add_stat("Level",2)
storage_2.add_stat("Material",0)
storage_2.add_stat("Max Material",1000)
storage_2.add_stat("Health",100)
factory = Card("Factory")
factory.add_stat("Max Level",3)
factory.add_stat("Energy Flow",-5)
factory.add_stat("Material Flow",-10)
factory.add_stat("Health",100)
factory.add_stat("Starbit Flow",10)
factory_2 = Card("Factory")
factory_2.add_stat("Level",2)
factory_2.add_stat("Energy Flow",-15)
factory_2.add_stat("Material Flow",-20)
factory_2.add_stat("Health",100)
factory_2.add_stat("Starbit Flow", 50)
factory_3 = Card("Factory")
factory_3.add_stat("Level",3)
factory_3.add_stat("Energy Flow",-32)
factory_3.add_stat("Material Flow",-45)
factory_3.add_stat("Health",100)
factory_3.add_stat("Starbit Flow", 120)
generator = Card("Generator")
generator.add_stat("Max Level",3)
generator.add_stat("Energy Flow",12)
generator.add_stat("Health",100)
generator_2 = Card("Generator")
generator_2.add_stat("Level",2)
generator_2.add_stat("Energy Flow",36)
generator_2.add_stat("Health",100)
generator_3 = Card("Generator")
generator_3.add_stat("Level",3)
generator_3.add_stat("Energy Flow",64)
generator_3.add_stat("Health",100)
hyperbeam = Card("Hyperbeam")
hyperbeam.add_stat("Max Level",2)
hyperbeam.add_stat("Energy Flow",-16)
hyperbeam.add_stat("Range",30)
hyperbeam.add_stat("Damage",45)
hyperbeam.add_stat("Health",100)
hyperbeam_2 = Card("Hyperbeam")
hyperbeam_2.add_stat("Level",2)
hyperbeam_2.add_stat("Energy Flow",-48)
hyperbeam_2.add_stat("Range",50)
hyperbeam_2.add_stat("Damage",90)
hyperbeam_2.add_stat("Health",100)
regenerator = Card("Regenerator")
regenerator.add_stat("Energy Flow",-20)
## prioritizes healing the core before anything around it
regenerator.add_stat("Range",60)
regenerator.add_stat("Health Flow",20)
regenerator.add_stat("Health",100)
booster = Card("Booster")
booster.add_stat("Energy Flow",-7)
booster.add_stat("Range",10)
booster.add_stat("Health",100)
energy_storage = Card("Energy Storage")
energy_storage.add_stat("Max Level",2)
energy_storage.add_stat("Energy",0)
energy_storage.add_stat("Max Energy",300)
energy_storage.add_stat("Health",100)
energy_storage_2 = Card("Energy Storage")
energy_storage_2.add_stat("Level",2)
energy_storage_2.add_stat("Energy",0)
energy_storage_2.add_stat("Max Energy",600)
energy_storage_2.add_stat("Health",100)
# </editor-fold>

# <editor-fold desc="Links for Upgrades">
laser_drill_2.set_upgrade(laser_drill_3)
factory_2.set_upgrade(factory_3)
generator_2.set_upgrade(generator_3)
laser_drill.set_upgrade(laser_drill_2)
factory.set_upgrade(factory_2)
generator.set_upgrade(generator_2)
storage.set_upgrade(storage_2)
energy_storage.set_upgrade(energy_storage_2)
hyperbeam.set_upgrade(hyperbeam_2)
# </editor-fold>

# TODO:
    # Make a sidebar where the minimized deck is shown on the left
    # | and you can choose to maximize any card at a given time
    # | while the options menu, cycle results, and other outputs are shown on the right
    # | this should somehow be possible using advanced python formatting tricks

# reconcile the settings and cheat code menus
# | cheat codes should allow for changing starbits and such
    # position is 1D instead of 2D
    # | each card spans a width of 10 <12> units
# functional 'combat' system
# | enemies add negative health flow
# | they spawn at the edges of the deck
# | deals damage to adjacent buildings
# | may have levels in the future
# | stats: health, damage
# | goal: to reach the core
# | enemies can pass destroyed structures
# | building more structures will just place around the enemy
# | you cannot sell enemies
# | can only be killed when health drops below 0
# | drop a small amount of starbits and / or energy
# when a building drops below 0 health,
# | it is 'destroyed' and non-functional
# | can only be sold for half the sell price
# | stats: selling price
# selling price stats could be made visible on the left when in the sell menu
# shield structure
# | absorbs a set amount of damage around it
# | small-medium range
# booster revamp
# | can boost the stats of any structure
# | could/should be extremely overpowered
# | therefore it should have an extra small range
# | where the range should be 12 except for the
# | highest level, where it can be 24
# | structures under the effect may be blue or magenta
# | oh, and boosters can stack effects
# | they also increase stats proportionally
# | probably 50% where the final numbers (after the stacking) are rounded down
# | boosters cannot boost each other
# booster effects include:
# | +hyperbeam damage
# | +regeneration amount
# | +laser drill material flow
# | +shield damage absorption
# | +factory starbit flow
# | +all the core stats
# regeneration structures: medium range
# | only heal structures in their range to make them balanced
# | buildings it regenerates may have a green name
# hyperbeam structures: medium range
# | they deal set damage to enemies in range
# | they can only fire in one direction
# | that direction is decided by whichever side has more enemies
# | and the tiebreaker is whichever side has more health
# research tree
# | each structure can be upgraded independently,
# | but you have to unlock each level in order.
# | the price in starbits is astronomical
# | and increases at insane amounts
# game progression
# | could be represented by the level of the core
# | where core research cost more than just starbits
# | completing research will ask for confirmation
# upgrades
# | generally be cheaper than the corresponding research
# | only require starbits
# | sell value of the building increases
# make the buy/sell price a stat of each structure
# remove redundant information in levelling structure
# checking stats by maximizing/minimizing structures will not count as an action
# during an action:
# | enemies can move or deal damage
# | enemies can be killed
# | structures can lose damage / be destroyed
# | buildings can be switched around (except the core)
# | energy is produced / consumed
# | material is produced / consumed
# | starbits are produced from material
# | structures may be upgraded
# | upgrades may be researched
# | structures may be bought / sold
# | you could sit back and watch your factory get destroyed
# when placing a building, you have the option of building up (above the core) or down (below the core)
# | this adds strategy, but now the core will rarely be found at index 0
# restrict starbits and health from going negative (do this at the very end, and make it a setting)
# | if the core's health drops below 0, it's GG
# | but if the core reaches a certain level, you win
# | exact cost is uncertain, but a million to trillion starbits needed
# | after beating the game, the secret code to unlocking cheats is shown
# | which unlocks special modes that add modifiers, which can be pretty funny
# modifiers:
# | buy and sell cores
# | infinite starbits, material, and / or energy
# | modify stats for buildings, or add your own
# | control over enemy mechanics
# | LVL4 pocket dimension: 12 cards
# | pocket dimensions can contain boosters, regenerators, shields, and even more pocket dimensions
# | you can move the core, even into pocket dimensions
# | new building: starbit generators
    # convenience for adding/modifying the base structures
    # | please
    # | it will make your life so much easier
# buildings should display more details about their status
# | active
# | inactive ( material, energy, idle )
# | health bars would look amazing
# different buildings may be conditionally idle and can be IDLE, ACTIVE, UNPOWERED, or NO MATERIAL:
# | generators: energy reserves are full
# | regenerators: surrounding health is full
# | laser drill: material storage is full
# | hyperbeam: not dealing damage (therefore they should take more energy when active)
# these buildings can never be idle, only ACTIVE or UNPOWERED:
# | boosters
# | shields
# these buildings merely exist as a STORAGE state:
# | storage
# | energy storage
# these buildings can only be active:
# | core
# | pocket dimension
# when storage structures are destroyed, we will attempt to transfer their contents
# | to other compatible storage structures, but any excess contents will be lost
# | you cannot sell a storage structure that is not empty
# selling buildings should also return only half the buy price
# | otherwise, you could sell a building right before it is destroyed and simply rebuy it
# it would make sense for structures to have different maximum health points
# energy flow should prioritize powering buildings closest to the core, and the top is the tiebreaker
# you can DEACTIVATE / REACTIVATE structures so that they won't consume energy
# | this does not count as an action and you can do this to as many structures as you like
# | a deactivated structure will have a faded name and white stats
# | they will not operate until they are reactivated
# Building status precedence:
# | DESTROYED: black
# | DEACTIVATED: grey
# | UNPOWERED / NO MATERIAL: red
# | boosted + shielded + regen: magenta
# | boosted + (shielded / regen): green
# | boosted: yellow
# | regen + shielded: cyan
# | shielded: blue
# | regen: green
# | IDLE / ACTIVE / STORAGE: white
# pocket dimension: a unique structure that compresses spacetime to increase building coverage!
# | LVL1 - 2 CARDS | LVL2 - 3 CARDS | LVL3 - 4 CARDS |
# | this works because each building inside will have a size of 12/NUM_CARDS units
# | boosters, regenerators, shields, and other pocket dimensions cannot be put inside.
# | when boosted, the pocket dimension will be blue
# | pocket dimension require an enormous amount of energy. At least 100-300 for LVL1
# | each stat will be printed specially and only be the slot of a card
# | there will be no empty slots: even at max level, if there are only 2 cards, each will be 6 units wide
# | if a pocket dimension collapses, instead of becoming UNPOWERED, it self-destructs.
# | There is no destroyed variant, it simply unpockets all structures in the order they were in.
# | Pocket dimensions start out empty, and you can move a structure into them if there is space
# | you can also swap out a structure inside the pocket dimension with a structure outside of it
# | The entire point of the pocket dimension, if it wasn't obvious, is to have more structures covered within a smaller space
# | Boosters, regenerators, and shields will affect all structures within the pocket dimension
# | But enemies can attack all structures within it at the same time
# | If all buildings within a pocket dimension are destroyed, it does not collapse, but enemies can pass it
# | The core cannot be moved, so it cannot be put inside of a pocket dimension
# position solution: instead of directly using the index in the array, access cards by their unique order (not position) in the deck.
# | this lets us access cards with a negative value
# | the core can keep its card index of 0
# | it skips over the pocket dimension, so you can access cards within the dimension separately
# | enemies are part of the order, but should be ignored for most cases
# enemy passage: if building health is below 50%, it is displayed as 'damaged' and enemies can pass through it
# after finishing cleaning up the code, implementing the pocket dimension should be a breeze.
# shop:
# | replaces the deck display with a collapsed list of structures + prices
# | selecting an item will maximize it, showing normally hidden stats such as level and max level
# | viewing the research tree works the same way
# | sell will also let you preview similar to the home screen
# the structure space will probably be longer than the output space, but both will be bottom-centered.
# | at the top of every screen will be a horizontal border '-=*=-=*=-=*=-=*=-=*=-' to distinguish between frames
# \/    //    #     \\    ]
# /\    \\    #     //    [
# \/    //    #    //     ]
# /\    \\    #    \\     [
# actions should have hotkeys for efficiency
# | typing '->' should automatically continue
# | '+-+' = shop
# | '$-$' = sell
# | '$' = sell focused
# | '=-=' = home
# | any +/0/- number in the home: maximize and focus that card (usually saves focus)
# | # + any number + # will focus on that card in the home screen
# | '#-#' = home screen with all cards minimized
# | '|>' = play
# | '||' = pause
# | '[]' = stop
# | '*-*' = upgrade
# | '*' = upgrade focused
# | '!-!' = research
# | '>-<' = move
# | '>' = move focused
# | make a process input function!
# | the single-key shortcuts will ask for a confirmation
# | '<-' functions as a cancellation
# by switching to terminal emulation..
# | keypresses aren't entered unless you use input()!
# | you don't need to press Enter for keyboard detection!
# | the entire console auto-scrolls instantly!
# add some info to buildings in the buy menu on the right for new players
# make sure to make research actually relevant
# could laser drills and generators have a very small material / energy storage ?
# research unlocks with xp?
# add a timer to show once the game is complete
# add more fun stats such as
# | buildings bought
# | final structure count
# | structures destroyed
# | enemies destroyed
# | total stuff production / consumption
# | (buying buildings = negative starbit consumption)
# | in the shop, buying is an action, so it should trigger a cycle that could show a negative starbit flow in the summary due to buying
# If we can get a measure of how advanced a factory is, we can introduce enemies at the right time, and level them up with the player
# factors for determining enemy presence from peaceful to apocalyptic:
# | total structures
# | starbit flow
# | highest starbits reached
# | damage per cycle
# | core level
# could the core level be the limiting criteria for researching?
# upgrades + research have to at least cost starbits, or the game is broken!!!
# more levels because the number of structures increases like crazy
# could research also unlock new buildings, like the pocket dimension?
# There should be an automatic 'upgrade this' feature or a 'upgrade as many of these possible' feature
# end at 10K-20K, 1M is theoretically possible but too tedious to be fun to reach
# | the problem is that the factory production peaks at around 1K, because LVL3 factories require insane amounts of
# | material and energy that it takes so long just to add 1 more of them to the production chain
# | which is okay, because the focus should be shifted to keeping the core alive from enemies
# | otherwise, just trying to earn starbits gets repetitive and forces you to build dozens (I have 24) of structures
# | just for a small +120 increase in starbit flow; Building this many buildings makes it too easy to prevent enemies
# | from reaching the core. If it has to get through 12 buildings, that's going to take a while even without weapon structures
# | but then again, by the 5K-10K starbit mark, (+700 - +1000) enemies should be at max level
# | only 27 lines can be displayed, so the number of structure slots should be limited to 25 (so enemies can still show up on edges)
# | but one should also be mindful of how many lines a maximized structure is (4-6)
# | at 70% zoom, 41 lines can be displayed vertically
# reduce the number of stat lines
# | right now, the core displays 11 stats
# | hide the level/max level (-2)
# | merge the resource/max resource stat display (-3)
# | that will reduce info lines down to 6
# | but each should also have a status line
# | to be more compact, a health bar could be put beside the structure name
# | generator: 4 -> 2
# | laser drill: 6 -> 3
# | factory: 7 -> 5
# | storage: 4 -> 1
# also, clean up the cycle statements to be cleaner
# | for transfers, just do {sender} {color}->{reset} {receiver} ({amount}/{max})


# Pocket Structures 2
# Make a function that attempts to transfer a required amount all of a certain resource, from nearest to farthest, into a certain structure's base resources.
# Make a function that gets all available resources of a certain kind across the entire structure space.
# Rearrange stats: Health (GREEN), Material (CYAN), Energy (BLUE), and Starbits (MAGENTA)
# Rename 'material' to 'stuff'
# Make the leveled-up structure tag look cleaner and less rare when in abundance
# | levels can be shown even at LVL1, but are white except when at MAX LVL, when they become magenta and override most (positive) status colors

# each argument that isn't empty should be an array of size l
# None means the stat shouldn't exist, while 0 still sets a starting value



# 1 drill 1 factory 3 generators

def full_house():
    deck.add_card(core)
    deck.add_card(laser_drill)
    deck.add_card(factory)
    deck.add_card(generator)
    deck.add_card(hyperbeam)
    deck.add_card(storage)
    deck.add_card(energy_storage)
    deck.add_card(regenerator)
    deck.add_card(booster)

deck.add_card(core)
'''deck.add_card(generator,7)
deck.add_card(factory,3)
deck.get_card(0).add_stat("Material",0)
deck.get_card(0).add_stat("Energy",50)
deck.get_card(0).add_stat("Health",900)
deck.add_card(laser_drill,20)
deck.add_card(storage)
deck.get_card(10).add_stat("Material",storage.stat("Max Material"))'''
#for n in range(1,7): deck.upgrade_card(n)
#deck.upgrade_card(0)
#deck.cycle()
#print(deck)
# 10 Material [0] Core -> [2] Factory
inventory = \
    [
        [999, "Core", core],
        [100, "Generator", generator],
        [200, "Factory", factory],
        [250, "Laser Drill", laser_drill],
        [300, "Storage", storage],
        [400, "Energy Storage", energy_storage],
        [600, "Hyperbeam", hyperbeam],
        [600, "Regenerator", regenerator],
        [900, "Booster", booster],
    ]
def shop():
    print("Card Shop")
    for i in range(int(CORE_SAFETY),len(inventory)):
        print("{0:<20}{1:>5}".format(f"[{i}] {inventory[i][1]}",f"| {magenta}{inventory[i][0]}{reset}"))
    answer = input("Which card would you like to buy? ")
    if not answer.isdigit():
        print(f"{red}You can't buy that card!{reset}")
        return
    answer = int(answer)
    # if the core is not buyable, then it will not be in the range
    if not answer in range(int(CORE_SAFETY),len(inventory)):
        print(f"{red}You can't buy that card!{reset}")
        return
    if deck.CORE.stat("Starbits") < inventory[answer][0]:
        print(f"{red}Not enough starbits!{reset}")
        return
    purchase = inventory[answer][2]
    deck.add_card(purchase)
    print(f"You bought \n{deck.last_card()} \nfor {magenta}{inventory[answer][0]}{reset} starbits")
    deck.add_starbits(-inventory[answer][0])

def cheat_codes():
    print(f"{yellow}Warning: not error-proof{reset}")
    deck.compact_list()
    ans = input("Please choose a card. ")
    try: ans = int(ans)
    except ValueError: ans = -1
    if not ans in range(0,deck.card_count()):
        print(f"{red}Could not find the card you are looking for.{reset}")
        return
    card = deck.get_card(ans)
    print(card)
    stat = input("Which stat would you like to modify/add? ")
    value = input("What value will you change it to? (Press Enter to remove) ")
    if value != "":
        card.add_stat(stat,int(round(float(value))))
    else:
        if stat in card.get_stats():
            card.get_stats().pop(stat)
    print(f"{card.get_name()} has been updated..")
    print(card)

def stats():
    ans = input("Which card would you like to view? ")
    try: ans = int(ans)
    except ValueError: ans = -1
    if not(ans in range(0,deck.card_count())):
        print(f"{red}Could not find the card you are looking for.{reset}")
        return
    print(deck.get_card(ans))

def sell():
    deck.compact_list()
    ans = input("Which card would you like to sell? ")
    try: ans = int(ans)
    except ValueError: ans = -1 # not in range
    # the card we are selling must be in range of the last card and/including the core
    if not ans in range(int(CORE_SAFETY),deck.card_count()):
        print(f"{red}You can't sell that card!{reset}")
        return
    card = deck.rem(ans)
    sell_price = 0
    for item in inventory:
        if card.name == item[1]:
            sell_price = item[0]
    deck.add_starbits(sell_price)
    print(f"You sold \n{card} \nfor {magenta}{sell_price}{reset} starbits")

research_lvl = 1
def research():
    global research_lvl
    match research_lvl:
        case 1:
            print(f"{generator.get_name()} can now be upgraded to {generator_2.get_name()}!")
        case 2:
            print(f"{generator_2.get_name()} can now be upgraded to {generator_3.get_name()}!")
        case _:
            print(f"{magenta}You have completed all possible research!{reset}")
    research_lvl += 1

def upgrade():
    deck.compact_list()
    ans = input("Which card would you like to upgrade? ")
    try: ans = int(ans)
    except ValueError: ans = -1
    if not ans in range(0,deck.card_count()):
        print(f"{red}You can't upgrade that card!{reset}")
        return
    sell_price = 0
    for item in inventory:
        if deck.get_card(ans).name == item[1]:
            sell_price = item[0]
    # factorial increase
    for i in range(1,deck.get_card(ans).stat("Level") + 1):
        sell_price *= (i + 1)
    difference = deck.CORE.stat("Starbits") - sell_price
    if difference < 0:
        print(f"{red}Not enough starbits! You have {magenta}{deck.CORE.stat("Starbits")}/{sell_price}{red} starbits!{reset}")
        return
    deck.add_starbits(-sell_price)
    deck.upgrade_card(ans)

def colored_switch(value):
    return f"{green if value else red}{str(value).upper()}{reset}"

def settings():
    global CORE_SAFETY
    global HIDDEN_STATS
    print("Welcome to the settings menu")
    print(f"[1] CORE_SAFETY: {colored_switch(CORE_SAFETY)}")
    print(f"[2] HIDDEN_STATS: {colored_switch(HIDDEN_STATS)}")
    ans = input("Please choose an option: ")
    try: ans = int(ans)
    except ValueError: ans = -1
    if not ans in range(1,3):
        print(f"{red}Not an option!{reset}")
    match ans:
        case 1:
            CORE_SAFETY = not CORE_SAFETY
            print(f"Changed CORE_SAFETY to {colored_switch(CORE_SAFETY)}")
        case 2:
            HIDDEN_STATS = not HIDDEN_STATS
            print(f"Changed HIDDEN_STATS to {colored_switch(HIDDEN_STATS)}")

def move():
    deck.compact_list()
    ans = input("Which card would you like to move? ")
    try: ans = int(ans)
    except ValueError: ans = -1
    if not ans in range(int(CORE_SAFETY),deck.card_count()):
        print(f"{red}You can't move that card!{reset}")
        return
    card = deck.get_card(ans)
    ans = input(f"{card.get_name()} is currently at {card.get_xy()},\nwhere would you like to move it? ")
    string = ans
    if string[0] in ["[","(","{"]: string = string[1:]
    if string[-1] in ["]",")","}"]: string = string[:-1]
    string = string.split(",",1)
    if len(string) == 2:
        if string[0].isdigit() and string[1].isdigit():
            x = int(string[0])
            y = int(string[1])
            card.move(x,y)
            print(f"{card.get_name()} has been moved to {card.get_xy()}")
            return
    print(f"{red}Invalid coordinates received. Cancelling movement..{reset}")

def reset_deck():
    global deck
    deck = Deck()
    deck.add_card(core)
    print(deck)
count = 1
deck.add_starbits(1000)
#deck.add_card(generator)
def main():
    global count
    print(f"\nTurn {count}")
    print("What action would you like to do?")
    options = ["Check deck","Card stats","Card shop","Sell cards","Reposition","Reset","Research","Cheat codes","Run all","Settings","Upgrades","Exit"] # time replaces achievements
    for i in range(6):
        print("{0:28}{1:7}".format(f"[{i*2 if i<5 else "+"}] {options[i*2 if i<5 else 10]}",f"[{i*2+1 if i<5 else "-"}] {options[i*2+1 if i<5 else 11]}"))

    ans = input()
    if ans in ["+","-"]: ans = 10 if ans == "+" else 11
    try: ans = int(ans)
    except ValueError: ans = 12
    match ans:
        case 0: print(deck)
        case 1: stats()
        case 2: shop()
        case 3: sell()
        case 4: move()
        case 5: reset_deck()
        case 6: research()
        case 7: cheat_codes()
        case 8: deck.cycle()
        case 9: settings()
        case 10: upgrade()
        case 11: return True
        case _: deck.cycle()
    #deck.cycle()
    if deck.CORE.stat("Starbits") >= 15000:
        global CONTINUE
        print(f"{magenta}YOU WIN!{reset}")
        print(f"Turns: {count}")
        print(f"Time: {time.time() - start_time}")
        if not CONTINUE:
            while True:
                ans = input("End game? ")
                ans = ans.lower()
                if ans in ["no","yes"]:
                    if ans == "no":
                        break
                    else:
                        return True
        CONTINUE = False
    input("Press Enter to continue.. ")
    count += 1
    return False
while True:
    if main(): break
print("Thanks for playing Pocket Structures!")