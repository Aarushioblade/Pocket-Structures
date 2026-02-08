from pynput import keyboard as kb
from calculator import Game, Shop, Research
from card import Card
from menu import Menu
from display import Display, Panel, InfoPanel
from stuff import Box
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
shop_panel = Panel(60)
info_panel = InfoPanel(35)
display.add(info_panel, home_panel, shop_panel, game.log)
structure_to_swap: Card | None = None
shift_held: bool = False
caption: str = ""

info_panel.load("intro")
shop_panel.hide()
game.log.hide()

def move(direction: int):
    global caption
    if menu is Menu.HOME:
        game.change_card_index(direction)
        card = game.deck.cards[game.card_index]
        info_panel.load(card.name)
    elif menu is Menu.SHOP:
        caption = shop.change_index(direction)
        shop_panel.clear()
        shop_panel.write(shop.display())
        shop_panel.write('\n')
        shop_panel.set(caption)
        info_panel.load(shop.selected_card().name)
    elif menu is Menu.RESEARCH:
        caption = research.change_index(direction)
        shop_panel.clear()
        shop_panel.write(research.display())
        shop_panel.write('\n')
        shop_panel.set(caption)
        info_panel.load(research.selected_card().name)
    elif menu is Menu.SELL:
        game.change_card_index(direction)
        card = game.deck.cards[game.card_index]
        if card.is_interactable or card.is_destroyed():
            caption = f"SELL: Selling {card} for {card.sell_price()}"
        else:
            if card.is_enemy:
                caption = f"SEll: Who's buying this?"
            elif card.is_core:
                caption = f"SELL: You can't sell the core"
            else:
                caption = f"SELL: This structure cannot be sold"
        shop_panel.set(caption)
        info_panel.load(card.name)
    elif menu is Menu.UPGRADE:
        game.change_card_index(direction)
        card = game.deck.cards[game.card_index]
        if card.at_max_level():
            caption = f"UPGRADE: {card} cannot be levelled up any further"
        elif not card.next_level_unlocked():
            caption = f"UPGRADE: {card} has not unlocked [LVL{card.level + 1}]"
        else:
            caption = f"UPGRADE: {card} -> [LVL{card.next_stats().level}] for {card.next_stats().price}"
        shop_panel.set(caption)
        info_panel.load(card.name)
    elif menu is Menu.SWAP:
        game.change_card_index(direction)
        card = game.deck.cards[game.card_index]
        shop_panel.clear()
        if card.is_destroyed() or not card.is_interactable:
            if structure_to_swap:
                shop_panel.write("Swap")
                shop_panel.write(structure_to_swap.display(True).display())
            caption = f"SWAP: {card} cannot be moved"
        else:

            shop_panel.write("Swap")
            if structure_to_swap and structure_to_swap != card:
                caption = f"SWAP: Swap {structure_to_swap} with {card}"
                shop_panel.write(structure_to_swap.display(True).display())
                shop_panel.write("with")
            else:
                caption = f"SWAP: Swap {card}"
            shop_panel.write(card.display(True).display())
        shop_panel.write("\n")
        shop_panel.set(caption)
        info_panel.load(card.name)


def switch_direction(direction: int):
    if menu is Menu.SHOP:
        direction = False if direction == -1 else True
        game.set_build_direction(direction)
    elif not game.log.hidden:
        game.log.flip_page(direction)


def exit_menu():
    set_menu(menu.HOME)
    global structure_to_swap
    structure_to_swap = None
    shop_panel.clear()
    shop_panel.hide()
    game.calculate()
    global caption
    caption = ""


def space():
    global caption
    global structure_to_swap
    match menu:
        case Menu.HOME:
            exit_menu()

        case Menu.SHOP:
            if game.can_buy(shop.selected_card().stats().price):
                set_menu(Menu.SHOP_CONFIRM)
                caption = f"CONFIRM: You are buying {shop.selected_card()}"
            else:
                caption = f"SHOP: Cannot buy {shop.selected_card()}"
            shop_panel.set(caption)

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
            shop_panel.set(caption)

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
            shop_panel.set(caption)

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
            else:
                caption = f"UPGRADE: Cannot upgrade {card}"
            shop_panel.set(caption)

        case Menu.UPGRADE_CONFIRM:
            game.upgrade(game.card_index)
            exit_menu()

        case Menu.SWAP:
            global structure_to_swap
            card = game.deck.cards[game.card_index]
            if card.is_destroyed() or not card.is_interactable:
                caption = f"SWAP: {card} cannot be moved"
            elif structure_to_swap:
                set_menu(Menu.SWAP_CONFIRM)
                caption = "SWAP: Confirm?"
            else:
                structure_to_swap = card
                caption = f"SWAP: Select another card to swap {card} with"
            shop_panel.set(caption)

        case Menu.SWAP_CONFIRM:
            swap_index = game.deck.index_of(structure_to_swap)
            game.swap(swap_index, game.card_index)
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
            shop_panel.hide()
    move(0)


def set_menu(new_menu: Menu):
    global menu
    menu = new_menu


def shop_menu():
    set_menu(menu.SHOP)
    shop_panel.clear()
    shop_panel.show()
    shop_panel.write(shop.display())
    move(0)


def sell_menu():
    set_menu(menu.SELL)
    shop_panel.clear()
    shop_panel.show()
    shop_panel.write("Select a structure to sell")
    move(0)


def research_menu():
    set_menu(menu.RESEARCH)
    shop_panel.clear()
    shop_panel.show()
    shop_panel.write(research.display())
    move(0)


def upgrade_menu():
    set_menu(menu.UPGRADE)
    shop_panel.clear()
    shop_panel.show()
    shop_panel.write("Select a structure to upgrade")
    move(0)


def swap_menu():
    set_menu(menu.SWAP)
    shop_panel.clear()
    shop_panel.show()
    global structure_to_swap
    structure_to_swap = None
    shop_panel.write("Select a structure to swap")
    move(0)


def log_menu():
    game.log.hidden = not game.log.hidden
    # game.log.add_stuff_filter(Box.Types.STARBIT.name)
    # game.log.clear_filters()


def help_menu():
    info_panel.hidden = not info_panel.hidden


def show_key_actions():
    string: str = ""
    if menu is Menu.HOME:
        string += "[UP/DOWN] Change Selection | "
        string += "[SPACE/ENTER] End Turn | "
        string += "[1] Shop | "
        string += "[2] Sell | "
        string += "[3] Research | "
        string += "[4] Upgrade | "
        string += "[5] Swap | "
        if game.log.hidden:
            string += "[6] Show Logs | "
        else:
            string += "[H-M] Select Filter | "
            string += "[SHIFT] Multi-Filter | "
            string += "[6] Close Logs | "
        if info_panel.hidden:
            string += "[7] Show Info "
        else:
            string += "[7] Close Info "
    else:
        string += "[UP/DOWN] Change Selection | "
        if menu in [Menu.SHOP_CONFIRM, Menu.SELL_CONFIRM, Menu.RESEARCH_CONFIRM, Menu.UPGRADE_CONFIRM]:
            string += "[SPACE/ENTER] Confirm | "
            string += "[TAB/DELETE] Go Back "
        else:
            match menu:
                case Menu.SHOP:
                    string += "[LEFT/RIGHT] Change build position | "
                    string += "[SPACE/ENTER] Buy | "
                case Menu.SELL:
                    string += "[SPACE/ENTER] Sell | "
                case Menu.RESEARCH:
                    string += "[SPACE/ENTER] Research | "
                case Menu.UPGRADE:
                    string += "[SPACE/ENTER] Upgrade | "

            string += "TAB/DELETE] Home "
    print(string, end="")


keybinds = {
    "UP": kb.Key.up,
    "DOWN": kb.Key.down,
    "LEFT": kb.Key.left,
    "RIGHT": kb.Key.right,
}


def match_key_to_filter(key: str):
    for stuff in Box.Types:
        if Box.keybinds[stuff] == key:
            return stuff
    return None


def change_filter(stuff: Box.Types):
    if stuff.name in game.log.stuff_fiter:
        game.log.rem_stuff_filter(stuff.name)
        return
    if not shift_held:
        game.log.clear_filters()
    game.log.add_stuff_filter(stuff.name)


def on_press(key):
    global menu
    try:
        key = key.char
        if key.isdigit():
            #print(f"digit {key}")
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
                case 5:
                    swap_menu()
                case 6:
                    log_menu()
                case 7:
                    help_menu()
        elif key.isalpha():
            key = key.upper()
            # print(f"alpha {key}")
            stuff_filter = match_key_to_filter(key)
            if stuff_filter:
                change_filter(stuff_filter)
    except AttributeError:
        match key:
            case kb.Key.up:
                move(-1)
            case kb.Key.down:
                move(1)
            case kb.Key.left:
                switch_direction(1)
            case kb.Key.right:
                switch_direction(-1)
            case kb.Key.enter | kb.Key.space:
                space()
            case kb.Key.tab | kb.Key.backspace | kb.Key.delete:
                back()
            case kb.Key.esc:
                return False
            case kb.Key.shift:
                global shift_held
                shift_held = True
    finally:
        home_panel.clear()
        home_panel.write(game.display(menu))
        display.render()
        show_key_actions()


def on_release(key):
    try:
        global shift_held
        if key == kb.Key.shift:
            shift_held = False
    except AttributeError:
        pass


with kb.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
