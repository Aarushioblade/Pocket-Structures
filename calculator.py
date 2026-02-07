import copy
import random

from card import Card
from deck import Deck
from display import Panel
from menu import Menu
from stuff import Box
from template import Template


class Game:
    def __init__(self, deck: Deck = None):

        self.build_direction: bool = False
        if deck is None: deck = Deck()
        self.deck: Deck = deck
        self.turn = 1
        self.card_index: int = 0
        self.log: Panel = Panel(55)
        self.deck.log = self.log
        self.enemy_spawn_rate = 0.05

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
        self.log.write(f"\n - Turn {self.turn} - \n")
        self.turn += 1

        for card in self.deck.sorted_by_distance():
            card.reset_status()

        for priority in range(0, 10):
            for card in self.deck.sorted_by_distance():
                if card.is_destroyed(): continue
                if card.priority != priority: continue
                if self.get_available_box() < card.inflow: continue
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

        if random.random() < self.enemy_spawn_rate:
            self.add_enemy()

    def can_buy(self, price: Box) -> bool:
        return not self.get_available_box() < price

    def buy(self, card: Card) -> None:
        if not self.can_buy(card.stats().price):
            raise Exception(f"Can't buy {card.name} for {card.stats().price}")
        card.log = self.log
        self.collect_purchase_from_other_cards(card)
        self.card_index = self.deck.add_card(card, is_below=self.build_direction)


    def sell(self, index: int) -> None:
        card = self.deck.cards[index]
        sell_price: Box = card.purchased * 0.75
        self.log.write(f"SELL: {card.name} >> {sell_price}")
        card.storage += sell_price
        self.store_to_other_cards(card)
        del self.deck.cards[index]
        if not self.card_index in range(len(self.deck.cards)):
            self.card_index = self.deck.cards.index(self.deck.get_core())

    def can_upgrade(self, index: int) -> bool:
        card = self.deck.cards[index]
        if card.level == len(card.levels):
            self.log.write(f"UPGRADE: {card.name} cannot be upgraded any further")
            return False
        if not card.next_stats().unlocked:
            self.log.write(f"UPGRADE: {card.name} has not unlocked level {card.level + 1}")
            return False
        if self.get_available_box() < card.next_stats().price:
            self.log.write(f"UPGRADE: {card.name} does not have enough resources to upgrade")
            return False
        return True

    def upgrade(self, index: int) -> None:
        card = self.deck.cards[index]
        if not self.can_upgrade(index):
            raise Exception(f"Can't upgrade {card.name}!")
        card_value = card.purchased.to_flow()
        card.purchased = Box()
        card.level_up()
        self.collect_purchase_from_other_cards(card)
        card.purchased += card_value

    def can_research(self, card: Card) -> bool:
        return not self.get_available_box() < card.stats().research_cost

    def research(self, card: Card) -> None:
        if not self.can_research(card):
            raise Exception(f"Can't research {card.name}!")
        levelled_card = copy.deepcopy(card)
        self.collect_research_from_other_cards(levelled_card)
        card.stats().unlocked = True
        self.log.write(f"RESEARCH: Unlocked level {card.stats().level} for {card.name}")

    def swap(self, i: int, j: int) -> None:
        temp: Card = self.deck.cards[i]
        self.deck.cards[i] = self.deck.cards[j]
        self.deck.cards[j] = temp
        self.log.write(f"SWAP: {self.deck.cards[j].name} <-> {self.deck.cards[i].name}")

    def change_card_index(self, amount: int) -> None:
        self.card_index += amount
        if self.card_index not in range(len(self.deck.cards)):
            # print(f"FOCUS: {self.card_index} is invalid")
            self.card_index -= amount
        card = self.deck.cards[self.card_index]
        # print(f"FOCUS: {self.card_index} ({card.name} LVL{card.level})")

    def set_build_direction(self, direction: bool) -> None:
        self.build_direction = direction
        #print(f"BUILD_UP: {self.build_direction}")

    def display(self, menu: Menu) -> str:
        string: str = ""
        in_shop: bool = menu == Menu.SHOP or menu == Menu.SHOP_CONFIRM
        if in_shop and not self.build_direction:
            string += "+ Preview \n"
        for index, card in enumerate(self.deck.cards):
            selected = index == self.card_index
            if selected:
                string += "= "
            else:
                string += "- "
            string += card.display(selected) + '\n'
            # string += str(card)
            # for line in card.display(selected).split("\n"):
            #    string += "    " + line + "\n"

        if in_shop and self.build_direction:
            string += "+ Preview \n"
        string = string.rstrip()
        return string

    def add_enemy(self):
        self.deck.add_card(Template.ENEMY.value, random.choice([True, False]))
        self.log.write("An enemy has spawned in!")


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
        string: str = ""
        for index, card in enumerate(self.inventory):
            if index == self.index:
                string += "> "
            string += f"{card} | "
            string += str(card.stats().price)
            string += '\n'
        string = string.rstrip()
        return string

    def select_message(self, card: Card) -> str:
        # card = self.inventory[self.index]
        return f"SHOP: Selecting {card} {card.stats().price}"


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
        string: str = ""
        for index, card in enumerate(self.inventory):
            if index == self.index:
                string += "> "
            string += f"{card} | "
            string += str(card.stats().research_cost)
            string += '\n'
        string = string.rstrip()
        return string

    def select_message(self, card: Card) -> str:
        return f"RESEARCH: Selecting {card} {card.stats().research_cost}"
