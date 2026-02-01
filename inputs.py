from enum import Enum

from pynput import keyboard as kb


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


def up():
    input_complete()


def down():
    input_complete()


def left():
    if menu not in [Menu.SHOP, Menu.RESEARCH]: return
    input_complete()


def right():
    if menu not in [Menu.SHOP, Menu.RESEARCH]: return
    input_complete()


def space():
    global menu
    if menu == Menu.HOME: return
    match menu:
        case Menu.SHOP:
            menu = Menu.SHOP_CONFIRM
        case Menu.SHOP_CONFIRM:
            menu = Menu.HOME
        case Menu.SELL:
            menu = Menu.SELL_CONFIRM
        case Menu.SELL_CONFIRM:
            menu = Menu.HOME
        case Menu.RESEARCH:
            menu = Menu.RESEARCH_CONFIRM
        case Menu.RESEARCH_CONFIRM:
            menu = Menu.HOME
        case Menu.UPGRADE:
            menu = Menu.UPGRADE_CONFIRM
        case Menu.UPGRADE_CONFIRM:
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


def on_press(key):
    try:
        key = key.char
    except AttributeError:
        match key:
            case kb.Key.up:
                up()
            case kb.Key.down:
                down()
            case kb.Key.left:
                left()
            case kb.Key.right:
                right()
            case kb.Key.enter | kb.Key.space:
                space()
            case kb.Key.tab | kb.Key.backspace | kb.Key.delete:
                back()
            case kb.Key.esc:
                return False
        return None
    if key.isdigit():
        print(f"digit {key}")
        key = int(key)
        global menu
        match key:
            case 0:
                pass
            case 1:
                menu = Menu.SHOP
            case 2:
                menu = Menu.SELL
            case 3:
                menu = Menu.RESEARCH
            case 4:
                menu = Menu.UPGRADE
        input_complete()
    elif key.isalpha():
        key = key.upper()
        print(f"alpha {key}")
    else:
        pass
    return None


def on_release(key):
    pass


with kb.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

if __name__ == "__main__":
    print("Press any key to register")
