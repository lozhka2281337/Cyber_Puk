import config as cfg

class World:
    def __init__(self):
        self.mod = cfg.NORMAL_MOD

        self.enemies = []
        self.bullets = []
        self.grenades = []
        self.effects = []
        self.walls = []
        self.pings = []

        # матрица карты
        self.matrix = []