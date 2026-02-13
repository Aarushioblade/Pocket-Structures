import copy
import random

from card import Card
from color import Color
from deck import Deck
from display import Info, LogPanel
from menu import Menu
from stuff import Box, Flow
from template import Template


# TODO:
# Increases in enemy difficulty
# Game over screen
# Win screen
# Fully upgradable card templates
# more accurate health bars
# known bug with researching everything

def color_text(text: str, color: Color) -> str:
    return f"{color.value}{text}{Color.WHITE.value}"

class Game:
    def __init__(self, deck: Deck = None):

        self.build_direction: bool = False
        if deck is None: deck = Deck()
        self.deck: Deck = deck
        self.turn = 1
        self.card_index: int = 0
        self.log: LogPanel = LogPanel(55)
        self.deck.log = self.log
        self.enemy_spawn_rate: float = 0.00

        self.menu: Menu = Menu.HOME

    def get_available_box(self) -> Box:
        available_box = Box()
        for card in self.deck.sorted_by_distance():
            if card.is_destroyed(): continue
            available_box += card.storage.to_flow()
        return available_box

    def store_to_other_cards(self, card: Card) -> None:
        for other in self.deck.sorted_by_distance(card):
            if other.is_destroyed(): continue
            if other == card: continue
            card.store(other)

    def collect_from_other_cards(self, card: Card) -> None:
        for other in self.deck.sorted_by_distance(card):
            if other.is_destroyed(): continue
            card.collect(other)

    def collect_purchase_from_other_cards(self, card: Card) -> None:
        for other in self.deck.sorted_by_distance():
            if other.is_destroyed(): continue
            card.collect_purchase(other)

    def collect_research_from_other_cards(self, card: Card) -> None:
        for other in self.deck.sorted_by_distance():
            if other.is_destroyed(): continue
            card.collect_research(other)

    def send_to_other_cards(self, card: Card) -> None:
        for target in self.deck.in_range(card):
            if target.is_destroyed(): continue
            card.send_to(target)

    def bonus_send_to_other_cards(self, card: Card) -> None:
        for target in self.deck.in_range(card):
            if target.is_destroyed(): continue
            card.bonus_send_to(target)

    def calculate(self) -> None:

        for card in self.deck.sorted_by_distance():
            card.reset_status()

        for priority in range(0, 10):
            for card in self.deck.sorted_by_distance():
                if card.is_destroyed(): continue
                if card.priority != priority: continue
                if card.requires_enemies:
                    if not self.enemies_in_range(card):
                        card.action = "IDLE"
                        continue
                if self.get_available_box() < card.inflow:
                    card.action = color_text("LACK RESOURCES", Color.RED)
                    # print out required
                    required: Box = self.get_available_box() - card.inflow
                    required: Flow = -required.to_flow().get_inflow()
                    # self.log.write(f"{Color.RED}{card} lacks resources!{Color.WHITE}")
                    for stuff in required.separate():
                        self.log.write(f"{stuff.accent()} {card} requires {stuff.value()} {stuff.name()}")
                    continue

                if card.is_enemy:
                    card.action = color_text("HOSTILE", Color.RED)
                else:
                    card.action = "ACTIVE"
                self.collect_from_other_cards(card)
                self.send_to_other_cards(card)
                card.produce()
                self.store_to_other_cards(card)

        for card in self.deck.sorted_by_distance():
            if card.is_destroyed(): continue
            self.bonus_send_to_other_cards(card)
            card.bonus_produce()
            self.store_to_other_cards(card)

        for card in self.deck.sorted_by_distance():
            card.reset_storage()

        for index, card in enumerate(self.deck.cards):
            if not card.is_enemy: continue
            if card.is_destroyed(): continue
            core_index = self.deck.index_of(self.deck.get_core())
            if index < core_index:
                direction = +1
            else:
                direction = -1
            other = self.deck.cards[index + direction]
            if other.is_destroyed() and not other.is_core:
                self.swap(index, index + direction)

        if random.random() < self.enemy_spawn_rate:
            self.add_enemy()

        if self.deck.get_core().is_destroyed():
            self.log.write(f"{Color.MAGENTA.value}CORE DESTROYED - GAME OVER!{Color.WHITE.value}")

        self.log.write(f"\n>> TURN {self.turn}\n")
        self.turn += 1

    def can_buy(self, price: Box) -> bool:
        return not self.get_available_box() < price

    def buy(self, card: Card) -> None:
        if not self.can_buy(card.stats().price):
            raise Exception(f"Can't buy {card.name} for {card.stats().price}")
        card.log = self.log
        self.collect_purchase_from_other_cards(card)
        self.card_index = self.deck.add_card(card, is_below=self.build_direction)
        self.log.write(f"| Constructed {card}")


    def sell(self, index: int) -> None:
        card = self.deck.cards[index]
        sell_price: Box = card.sell_price()
        for stuff in sell_price.separate():
            self.log.write(f"{stuff.accent()} {card} was sold for {stuff.value()} {stuff.name()}")
        card.storage += sell_price
        self.store_to_other_cards(card)
        del self.deck.cards[index]
        if not self.card_index in range(len(self.deck.cards)):
            self.card_index = self.deck.cards.index(self.deck.get_core())

    def can_upgrade(self, index: int) -> bool:
        card = self.deck.cards[index]
        if card.is_enemy: return False
        if card.level == len(card.levels):
            self.log.write(f"UPGRADE: {card} cannot be upgraded any further")
            return False
        if not card.next_stats().unlocked:
            self.log.write(f"UPGRADE: {card} has not unlocked [LVL{card.level + 1}]")
            return False
        if self.get_available_box() < card.next_stats().price:
            self.log.write(f"UPGRADE: {card} does not have enough resources to upgrade")
            return False
        return True

    def upgrade(self, index: int) -> None:
        card = self.deck.cards[index]
        if not self.can_upgrade(index):
            raise Exception(f"Can't upgrade {card}!")
        card_value = card.purchased.to_flow()
        card.purchased = Box()
        previous_card = str(card)
        card.level_up()
        self.collect_purchase_from_other_cards(card)
        card.purchased += card_value
        self.log.write(f"| Upgraded {previous_card} to [LVL{card.level}]")

    def can_research(self, card: Card) -> bool:
        return not self.get_available_box() < card.stats().research_cost

    def research(self, card: Card) -> None:
        if not self.can_research(card):
            raise Exception(f"Can't research {card.name}!")
        levelled_card = copy.deepcopy(card)
        levelled_card.log = self.log
        self.collect_research_from_other_cards(levelled_card)
        card.stats().unlocked = True
        if card.stats().level == 1:
            self.log.write(f"| {card.name} can now be constructed!")
        else:
            self.log.write(f"| {card.name} can now be upgraded to [LVL{card.stats().level}]")

    def swap(self, i: int, j: int) -> None:
        temp: Card = self.deck.cards[i]
        self.deck.cards[i] = self.deck.cards[j]
        self.deck.cards[j] = temp
        self.log.write(f"| Swapped {self.deck.cards[j]} with {self.deck.cards[i]}")

    def change_card_index(self, amount: int) -> None:
        self.card_index += amount
        if self.card_index not in range(len(self.deck.cards)):
            # print(f"FOCUS: {self.card_index} is invalid")
            self.card_index -= amount
        #card = self.deck.cards[self.card_index]
        # print(f"FOCUS: {self.card_index} ({card.name} LVL{card.level})")

    def set_build_direction(self, direction: bool) -> None:
        self.build_direction = direction
        #print(f"BUILD_UP: {self.build_direction}")

    def display(self, menu: Menu) -> str:
        string: str = ""
        in_shop: bool = menu is Menu.SHOP or menu is Menu.SHOP_CONFIRM
        if in_shop and not self.build_direction:
            string += "+ Preview \n"
        selected_card: Card = self.deck.cards[self.card_index]
        cards_in_range: list[Card] = self.deck.in_range(selected_card)
        for index, card in enumerate(self.deck.cards):
            selected = index == self.card_index
            if menu is Menu.SELL or menu is Menu.SELL_CONFIRM:
                if (card.is_destroyed() or not card.is_enemy) and not card.is_core:
                    value = str(card.sell_price().to_box())
                elif card.is_enemy:
                    value = "ENEMY"
                else:
                    value = "CORE"
            elif menu is Menu.UPGRADE or menu is Menu.UPGRADE_CONFIRM:
                if card.is_enemy:
                    value = "ENEMY"
                elif card.at_max_level():
                    value = "MAX LEVEL"
                elif not card.next_level_unlocked():
                    value = "LOCKED"
                else:
                    value = str(card.next_stats().price)
            else:
                if selected or card.missing_health():
                    value = card.health_bar()
                else:
                    value = ""
            prefix: str = "- "
            if selected: prefix = "= "
            if card.is_destroyed():
                prefix = color_text(prefix, Color.GRAY)
            if card.is_enemy or card.action.count(Color.RED.value):
                prefix = color_text(prefix, Color.RED)
            elif card in cards_in_range:
                for stuff in selected_card.stats().effect_flow.separate():
                    prefix = color_text(prefix, stuff.color())

            string += card.display(selected, width=48, name_value=value).display(prefix) + '\n'
            # string += str(card)
            # for line in card.display(selected).split("\n"):
            #    string += "    " + line + "\n"

        if in_shop and self.build_direction:
            string += "+ Preview \n"
        string = string.rstrip()
        self.menu = menu
        return string

    def add_enemy(self):
        enemy = self.deck.add_card(Template.ENEMY.value, random.choice([True, False]))
        self.card_index = enemy
        enemy_card = self.deck.cards[enemy]
        enemy_card.purchased = enemy_card.stats().price * 4
        self.log.write(f"{Color.RED.value}{enemy_card} has entered the base! {Color.WHITE.value}")

    def enemies_in_range(self, card: Card) -> bool:
        for other in self.deck.in_range(card):
            if other.is_enemy:
                if not other.is_destroyed():
                    return True
        return False


class Shop:
    def __init__(self) -> None:
        self.inventory: list[Card] = []
        self.index: int = 0
        self.update()

    def update(self):
        self.inventory.clear()
        for card in Template:
            if not card.value.is_interactable: continue
            if not card.value.stats().unlocked: continue
            self.inventory.append(card.value)
        self.index = 0

    def change_index(self, index: int) -> str:
        self.index += index
        if self.index not in range(len(self.inventory)):
            # print(f"SHOP: {self.index} is invalid")
            self.index -= index
        card = self.inventory[self.index]
        return self.select_message(card)

    def selected_card(self) -> Card:
        return copy.deepcopy(self.inventory[self.index])

    def display(self) -> str:
        info = Info(50)
        for index, card in enumerate(self.inventory):
            info.extend(card.display(index == self.index, name_value=str(card.stats().price)))
        return "SHOP\n\n" + info.display()

    def select_message(self, card: Card) -> str:
        # card = self.inventory[self.index]
        return f"SHOP: Selecting {card} for {card.stats().price}"


class Research(Shop):
    def update(self):
        self.inventory.clear()
        for card in Template:
            if not card.value.is_interactable: continue
            for level in card.value.levels:
                if level.unlocked: continue
                levelled_card = copy.deepcopy(card.value)
                levelled_card.level = level.level
                self.inventory.append(levelled_card)
                break
        self.index = 0

    def display(self) -> str:
        info = Info(50)
        for index, card in enumerate(self.inventory):
            info.extend(card.display(index == self.index, name_value=str(card.stats().research_cost)))
        return "RESEARCH\n\n" + info.display()

    def select_message(self, card: Card) -> str:
        return f"RESEARCH: Selecting {card} for {card.stats().research_cost}"
