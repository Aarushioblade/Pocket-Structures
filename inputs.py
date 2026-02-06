from enum import Enum

from pynput import keyboard as kb
from calculator import Game, Shop
from display import Display, Panel
from template import Template


class Menu(Enum):
    HOME = 0
    SHOP = 1
    SHOP_CONFIRM = 2
    SELL = 3
    SELL_CONFIRM = 4
    RESEARCH = 5
    RESEARCH_CONFIRM = 6
    UPGRADE = 7
    UPGRADE_CONFIRM = 8


menu: Menu = Menu.HOME
game = Game()
game.deck.add_card(Template.CORE.value)
shop = Shop()
research = Shop()
shop.update_shop()
research.update_research()


def move(direction: int):
    if menu in [Menu.HOME, Menu.SELL, Menu.UPGRADE]:
        game.change_card_index(direction)
    elif menu is Menu.SHOP:
        shop.change_shop_index(direction)
    elif menu is Menu.RESEARCH:
        research.change_shop_index(direction)
    home_panel.clear()
    home_panel.write(game.display())
    input_complete()


def switch(direction: bool):
    if menu is not Menu.SHOP: return
    game.set_build_direction(direction)
    input_complete()


def space():
    global menu
    if menu == Menu.HOME: return
    match menu:
        case Menu.SHOP:
            if game.can_buy(shop.selected_card().stats().price):
                menu = Menu.SHOP_CONFIRM
                print(f"CONFIRM: You are buying {shop.selected_card().name}")
            else:
                print(f"SHOP: Cannot buy {shop.selected_card().name}")
        case Menu.SHOP_CONFIRM:
            game.buy(shop.selected_card())
            menu = Menu.HOME
        case Menu.SELL:
            card = game.deck.cards[game.card_index]
            if card.is_interactable:
                menu = Menu.SELL_CONFIRM
                print(f"CONFIRM: You are selling {card.name}")
            else:
                print(f"SELL: Cannot sell {card.name}")
        case Menu.SELL_CONFIRM:
            game.sell(game.card_index)
            menu = Menu.HOME
        case Menu.RESEARCH:
            card = research.selected_card()
            if game.can_research(card):
                menu = Menu.RESEARCH_CONFIRM
                print(f"RESEARCH: You are researching level {card.stats().level} for {card.name}")
            else:
                print(f"RESEARCH: Cannot research {card.name}")
        case Menu.RESEARCH_CONFIRM:
            game.research(research.selected_card())
            research.update_research()
            shop.update_shop()
            menu = Menu.HOME
        case Menu.UPGRADE:
            card = game.deck.cards[game.card_index]
            if game.can_upgrade(game.card_index):
                menu = Menu.UPGRADE_CONFIRM
                print(f"UPGRADE: You are upgrading {card.name} to level {card.next_stats().level}")
        case Menu.UPGRADE_CONFIRM:
            game.upgrade(game.card_index)
            menu = Menu.HOME
    input_complete()


def back():
    global menu
    match menu:
        case menu.SHOP_CONFIRM:
            menu = Menu.SHOP
        case menu.SELL_CONFIRM:
            menu = Menu.SELL
        case menu.RESEARCH_CONFIRM:
            menu = Menu.RESEARCH
        case menu.UPGRADE_CONFIRM:
            menu = Menu.UPGRADE
        case _:
            menu = Menu.HOME
    input_complete()


def input_complete():
    print(menu)


def write_shop():
    shop_panel.clear()
    shop_panel.write("SHOP")
    shop_panel.write(shop.display())


def write_sell():
    shop_panel.clear()
    shop_panel.write("SELL")
    shop_panel.write("Select a building to sell")


def write_research():
    shop_panel.clear()
    shop_panel.write("RESEARCH")
    shop_panel.write(research.display())


def write_upgrade():
    shop_panel.clear()
    shop_panel.write("UPGRADE")
    shop_panel.write("Select a building to upgrade")


display = Display()
home_panel = Panel(30)
shop_panel = Panel(45)
display.add(home_panel, shop_panel)

def on_press(key):
    try:
        key = key.char
    except AttributeError:
        match key:
            case kb.Key.up:
                move(1)
            case kb.Key.down:
                move(-1)
            case kb.Key.left:
                switch(False)
            case kb.Key.right:
                switch(True)
            case kb.Key.enter | kb.Key.space:
                space()
            case kb.Key.tab | kb.Key.backspace | kb.Key.delete:
                back()
            case kb.Key.esc:
                return False
        display.render()
        return None
    if key.isdigit():
        print(f"digit {key}")
        key = int(key)
        global menu
        match key:
            case 0:
                pass
            case 1:
                print(shop.inventory)
                menu = Menu.SHOP
                write_shop()
            case 2:
                menu = Menu.SELL
                write_sell()
            case 3:
                print(research.inventory)
                menu = Menu.RESEARCH
                write_research()
            case 4:
                menu = Menu.UPGRADE
                write_upgrade()
        input_complete()
    elif key.isalpha():
        key = key.upper()
        print(f"alpha {key}")
    else:
        pass
    home_panel.clear()
    home_panel.write(game.display())
    display.render()
    return None


def on_release(key):
    pass


with kb.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

if __name__ == "__main__":
    print("Press any key to register")