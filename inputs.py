from _pyrepl.commands import home
from enum import Enum

from pynput import keyboard as kb
from calculator import Game, Shop, Research
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
research = Research()
shop.update()
research.update()

caption: str = ""

def move(direction: int):
    global caption
    if menu in [Menu.HOME, Menu.SELL, Menu.UPGRADE]:
        game.change_card_index(direction)
    elif menu is Menu.SHOP:
        caption = shop.change_index(direction)
        shop_panel.clear()
        shop_panel.write(shop.display())
    elif menu is Menu.RESEARCH:
        caption = research.change_index(direction)
        shop_panel.clear()
        shop_panel.write(research.display())


def switch(direction: bool):
    if menu is not Menu.SHOP: return
    game.set_build_direction(direction)


def exit_menu():
    set_menu(menu.HOME)
    shop_panel.clear()

def space():
    global caption
    if menu == Menu.HOME: return
    match menu:
        case Menu.SHOP:
            if game.can_buy(shop.selected_card().stats().price):
                set_menu(Menu.SHOP_CONFIRM)
                caption = f"CONFIRM: You are buying {shop.selected_card().name}"
            else:
                caption = f"SHOP: Cannot buy {shop.selected_card().name}"
        case Menu.SHOP_CONFIRM:
            game.buy(shop.selected_card())
            exit_menu()
        case Menu.SELL:
            card = game.deck.cards[game.card_index]
            if card.is_interactable:
                set_menu(Menu.SELL_CONFIRM)
                caption = f"CONFIRM: You are selling {card.name}"
            else:
                caption = f"SELL: Cannot sell {card.name}"
        case Menu.SELL_CONFIRM:
            game.sell(game.card_index)
            exit_menu()
        case Menu.RESEARCH:
            card = research.selected_card()
            if game.can_research(card):
                set_menu(Menu.RESEARCH_CONFIRM)
                caption = f"RESEARCH: You are researching level {card.stats().level} for {card.name}"
            else:
                caption = f"RESEARCH: Cannot research {card.name}"
        case Menu.RESEARCH_CONFIRM:
            game.research(research.selected_card())
            research.update()
            shop.update()
            exit_menu()
        case Menu.UPGRADE:
            card = game.deck.cards[game.card_index]
            if game.can_upgrade(game.card_index):
                set_menu(Menu.UPGRADE_CONFIRM)
                caption = f"UPGRADE: You are upgrading {card.name} to level {card.next_stats().level}"
        case Menu.UPGRADE_CONFIRM:
            game.upgrade(game.card_index)
            exit_menu()


def back():
    match menu:
        case menu.SHOP_CONFIRM:
            set_menu(Menu.SHOP)
        case menu.SELL_CONFIRM:
            set_menu(Menu.SELL)
        case menu.RESEARCH_CONFIRM:
            set_menu(Menu.RESEARCH)
        case menu.UPGRADE_CONFIRM:
            set_menu(Menu.UPGRADE)
        case _:
            set_menu(Menu.HOME)

display = Display()
home_panel = Panel(40)
shop_panel = Panel(45)
display.add(home_panel, shop_panel)


def set_menu(new_menu: Menu):
    global menu
    menu = new_menu


def shop_menu():
    set_menu(menu.SHOP)
    shop_panel.clear()
    shop_panel.write(shop.display())


def sell_menu():
    set_menu(menu.SELL)
    shop_panel.clear()
    shop_panel.write("Select a structure to sell")


def research_menu():
    set_menu(menu.RESEARCH)
    shop_panel.clear()
    shop_panel.write(research.display())


def upgrade_menu():
    set_menu(menu.UPGRADE)
    shop_panel.clear()
    shop_panel.write("Select a structure to upgrade")


def on_press(key):
    try:
        key = key.char
        if key.isdigit():
            print(f"digit {key}")
            key = int(key)
            global menu
            match key:
                case 0:
                    pass
                case 1:
                    shop_menu()
                case 2:
                    sell_menu()
                case 3:
                    research_menu()
                case 4:
                    upgrade_menu()
        elif key.isalpha():
            key = key.upper()
            print(f"alpha {key}")
    except AttributeError:
        match key:
            case kb.Key.up:
                move(-1)
            case kb.Key.down:
                move(1)
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
    finally:
        home_panel.clear()
        home_panel.write(game.display())
        display.render()
        global caption
        print(caption)
        caption = ""


with kb.Listener(on_press=on_press) as listener:
    listener.join()

if __name__ == "__main__":
    print("Press any key to register")