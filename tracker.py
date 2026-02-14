import copy

from stuff import Box


class Tracker:
    def __init__(self):
        self.production: Box = Box()
        self.bonus_production: Box = Box()
        self.consumption: Box = Box()
        self.demand: Box = Box()
        self.previous_storage: Box = Box()
        self.potential: Box = Box()
        self.storage: Box = Box()
        self.capacity: Box = Box()

    def reset(self):
        self.production = Box()
        self.bonus_production = Box()
        self.consumption = Box()
        self.demand = Box()
        self.previous_storage = copy.copy(self.storage)
