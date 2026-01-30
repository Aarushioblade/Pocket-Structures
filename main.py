from structures import Deck, Blueprints


def main():
    deck = Deck()
    deck += Blueprints.CORE
    deck += Blueprints.GENERATOR
    print(deck)


if __name__ == '__main__':
    main()

# TODO:
# negative flows should always be in red
