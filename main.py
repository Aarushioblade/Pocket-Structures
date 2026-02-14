from pynput import keyboard as kb
from calculator import Game, Shop, Research
from card import Card
from menu import Menu
from display import Display, Panel, InfoPanel, SummaryPanel
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
display.separator = " | "
display.height = 41
home_panel = Panel(50)
shop_panel = Panel(50)
info_panel = InfoPanel(35)
summary_panel = SummaryPanel(23, game.tracker)
display.add(info_panel, home_panel, summary_panel, shop_panel, game.log)
structure_to_swap: Card | None = None
shift_held: bool = False
game_started: bool = False
caption: str = ""
game_complete: bool = False

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
            caption = f"Selling {card} for {card.sell_price()}"
        else:
            if card.is_enemy:
                caption = f"Defeat it first!"
            elif card.is_core:
                caption = f"You can't sell the core..."
            else:
                caption = f"This structure cannot be sold"
        shop_panel.set(caption)
        info_panel.load(card.name)
    elif menu is Menu.UPGRADE:
        game.change_card_index(direction)
        card = game.deck.cards[game.card_index]
        if card.at_max_level():
            caption = f"{card} cannot be levelled up any further"
        elif not card.next_level_unlocked():
            caption = f"{card} has not unlocked [LVL{card.level + 1}]"
        elif not card.is_enemy:
            caption = f"{card} -> [LVL{card.next_stats().level}] for {card.next_stats().price}"
        else:
            caption = f"Please do not upgrade {card}"
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


message: str | None = None

def exit_menu():
    set_menu(menu.HOME)
    global structure_to_swap
    structure_to_swap = None
    shop_panel.clear()
    shop_panel.hide()
    global caption
    caption = ""
    global message
    global game_complete
    if not game_complete:
        message = game.calculate()
        summary_panel.rewrite()
        game.tracker.reset()
        if message:
            game_complete = True
            if message.lower().count("game over"):
                info_panel.load("game over")
                on_press(kb.Key.enter)
            elif message.lower().count("congratulations"):
                info_panel.load("game complete")
                on_press(kb.Key.enter)


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
                caption = f"Cannot buy {shop.selected_card()}!"
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
                caption = f"Cannot sell {card}!"
            shop_panel.set(caption)

        case Menu.SELL_CONFIRM:
            game.sell(game.card_index)
            exit_menu()

        case Menu.RESEARCH:
            if research.completed():
                caption = f"Congratulations! You have completed all available research!"
                shop_panel.set(caption)
                return
            card = research.selected_card()
            if game.can_research(card):
                set_menu(Menu.RESEARCH_CONFIRM)
                caption = f"CONFIRM: You are researching {card}"
            else:
                caption = f"Cannot research {card}!"
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
                caption = f"CONFIRM: You are upgrading {card} to [LVL{card.next_stats().level}]"
            else:
                caption = f"Cannot upgrade {card}!"
            shop_panel.set(caption)

        case Menu.UPGRADE_CONFIRM:
            game.upgrade(game.card_index)
            exit_menu()

        case Menu.SWAP:
            global structure_to_swap
            card = game.deck.cards[game.card_index]
            if card.is_destroyed() or not card.is_interactable:
                caption = f"{card} cannot be moved"
            elif structure_to_swap:
                set_menu(Menu.SWAP_CONFIRM)
                caption = f"CONFIRM: You are swapping {card} with {structure_to_swap}"
            else:
                structure_to_swap = card
                caption = f"Select another card to swap {card} with"
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
    if game_complete: return
    set_menu(menu.SHOP)
    shop_panel.clear()
    shop_panel.show()
    shop_panel.write(shop.display())
    move(0)


def sell_menu():
    if game_complete: return
    set_menu(menu.SELL)
    shop_panel.clear()
    shop_panel.show()
    shop_panel.write("Select a structure to sell")
    move(0)


def research_menu():
    if game_complete: return
    set_menu(menu.RESEARCH)
    shop_panel.clear()
    shop_panel.show()
    shop_panel.write(research.display())
    move(0)


def upgrade_menu():
    if game_complete: return
    set_menu(menu.UPGRADE)
    shop_panel.clear()
    shop_panel.show()
    shop_panel.write("Select a structure to upgrade")
    move(0)


def swap_menu():
    if game_complete: return
    set_menu(menu.SWAP)
    shop_panel.clear()
    shop_panel.show()
    global structure_to_swap
    structure_to_swap = None
    shop_panel.write("Select a structure to swap")
    move(0)


def summary_menu():
    summary_panel.hidden = not summary_panel.hidden

def log_menu():
    game.log.hidden = not game.log.hidden
    # game.log.add_stuff_filter(Box.Types.STARBIT.name)
    # game.log.clear_filters()


def help_menu():
    info_panel.hidden = not info_panel.hidden


def show_key_actions():
    global game_complete
    string: str = ""
    if menu is Menu.HOME:
        string += "[UP/DOWN] Change Selection | "
        if not game_complete:
            string += "[SPACE/ENTER] End Turn | "
            string += "[1] Shop | "
            string += "[2] Sell | "
            string += "[3] Research | "
            string += "[4] Upgrade | "
            string += "[5] Swap | "
        if summary_panel.hidden:
            string += "[6] Show Summary | "
        else:
            string += "[6] Close Summary | "
        if game.log.hidden:
            string += "[7] Show Logs | "
        else:
            string += "[QWERTY] Select Filter | "
            string += "[SHIFT] Multi-Filter | "
            string += "[7] Close Logs | "
        if info_panel.hidden:
            string += "[8] Show Info "
        else:
            string += "[8] Close Info "
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
    global message
    if message is not None:
        game_complete = True
        print('\n', message, end="", sep="")


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
    global game_started
    if not game_started:
        game_started = True
        key = kb.Key.enter
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
                    summary_menu()
                case 7:
                    log_menu()
                case 8:
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
            case kb.Key.shift | kb.Key.shift_r:
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
        if key in [kb.Key.shift, kb.Key.shift_r]:
            shift_held = False
    except AttributeError:
        pass


print("Press any key to start the game ", end="")

with kb.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()