from pynput import keyboard as kb
from calculator import Game, Shop, Research
from menu import Menu
from display import Display, Panel
from template import Template

menu: Menu = Menu.HOME
game = Game()
game.deck.add_card(Template.CORE.value)
shop = Shop()
research = Research()
shop.update()
research.update()
display = Display()
home_panel = Panel(50)
shop_panel = Panel(50)
display.add(home_panel, shop_panel, game.log)
caption: str = ""


def move(direction: int):
    global caption
    if menu is Menu.HOME:
        game.change_card_index(direction)
    elif menu is Menu.SHOP:
        caption = shop.change_index(direction)
        shop_panel.clear()
        shop_panel.write(shop.display())
    elif menu is Menu.RESEARCH:
        caption = research.change_index(direction)
        shop_panel.clear()
        shop_panel.write(research.display())
    elif menu is Menu.SELL:
        game.change_card_index(direction)
        card = game.deck.cards[game.card_index]
        if card.is_interactable or card.is_destroyed():
            caption = f"SELL: Selling {card} for {card.sell_price()}"
        else:
            caption = f"SELL: This card cannot be sold"
    elif menu is Menu.UPGRADE:
        game.change_card_index(direction)
        card = game.deck.cards[game.card_index]
        if card.at_max_level():
            caption = f"UPGRADE: {card} cannot be levelled up any further"
        elif not card.next_level_unlocked():
            caption = f"UPGRADE: {card} has not unlocked [LVL{card.level + 1}]"
        else:
            caption = f"UPGRADE: {card} -> [LVL{card.next_stats().level}] for {card.next_stats().price}"


def switch_direction(direction: bool):
    if menu is not Menu.SHOP: return
    game.set_build_direction(direction)


def exit_menu():
    set_menu(menu.HOME)
    shop_panel.clear()
    game.calculate()
    global caption
    caption = ""


def space():
    global caption
    match menu:
        case Menu.HOME:
            exit_menu()

        case Menu.SHOP:
            if game.can_buy(shop.selected_card().stats().price):
                set_menu(Menu.SHOP_CONFIRM)
                caption = f"CONFIRM: You are buying {shop.selected_card()}"
            else:
                caption = f"SHOP: Cannot buy {shop.selected_card()}"
        case Menu.SHOP_CONFIRM:
            game.buy(shop.selected_card())
            exit_menu()

        case Menu.SELL:
            card = game.deck.cards[game.card_index]
            if card.is_interactable or card.is_destroyed():
                set_menu(Menu.SELL_CONFIRM)
                caption = f"CONFIRM: You are selling {card}"
            else:
                caption = f"SELL: Cannot sell {card}"
        case Menu.SELL_CONFIRM:
            game.sell(game.card_index)
            exit_menu()

        case Menu.RESEARCH:
            card = research.selected_card()
            if game.can_research(card):
                set_menu(Menu.RESEARCH_CONFIRM)
                caption = f"RESEARCH: You are researching level {card.stats().level} for {card}"
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
                caption = f"UPGRADE: You are upgrading {card} to [LVL{card.next_stats().level}]"
        case Menu.UPGRADE_CONFIRM:
            game.upgrade(game.card_index)
            exit_menu()


def back():
    global caption
    caption = ""
    match menu:
        case menu.SHOP_CONFIRM:
            shop_menu()
        case menu.SELL_CONFIRM:
            sell_menu()
        case menu.RESEARCH_CONFIRM:
            research_menu()
        case menu.UPGRADE_CONFIRM:
            upgrade_menu()
        case _:
            set_menu(Menu.HOME)
            shop_panel.clear()


def set_menu(new_menu: Menu):
    global menu
    menu = new_menu


def shop_menu():
    set_menu(menu.SHOP)
    shop_panel.clear()
    shop_panel.write(shop.display())
    move(0)


def sell_menu():
    set_menu(menu.SELL)
    shop_panel.clear()
    shop_panel.write("Select a structure to sell")
    move(0)


def research_menu():
    set_menu(menu.RESEARCH)
    shop_panel.clear()
    shop_panel.write(research.display())
    move(0)


def upgrade_menu():
    set_menu(menu.UPGRADE)
    shop_panel.clear()
    shop_panel.write("Select a structure to upgrade")
    move(0)


def on_press(key):
    global menu
    try:
        key = key.char
        if key.isdigit():
            print(f"digit {key}")
            key = int(key)

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
                switch_direction(True)
            case kb.Key.right:
                switch_direction(False)
            case kb.Key.enter | kb.Key.space:
                space()
            case kb.Key.tab | kb.Key.backspace | kb.Key.delete:
                back()
            case kb.Key.esc:
                return False
    finally:
        home_panel.clear()
        home_panel.write(game.display(menu))
        display.render()
        print(caption)

with kb.Listener(on_press=on_press) as listener:
    listener.join()
