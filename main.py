from structures import Deck, Blueprints


def main():
    deck = Deck()
    deck += Blueprints.CORE
    deck += Blueprints.GENERATOR
    deck += Blueprints.MINE
    deck += Blueprints.FACTORY
    deck += Blueprints.STORAGE
    deck += Blueprints.HYPERBEAM
    deck += Blueprints.ENEMY
    deck += Blueprints.BOOST
    deck += Blueprints.REGENERATOR
    deck += Blueprints.SHIELD
    deck += Blueprints.BOOST
    for card in deck * (Blueprints.BOOST + Blueprints.CORE + Blueprints.ENEMY):
        print(card)


# deck*Blueprints.BOOST + deck*Blueprints.CORE == deck*(Blueprints.BOOST + Blueprints.CORE)

if __name__ == '__main__':
    main()