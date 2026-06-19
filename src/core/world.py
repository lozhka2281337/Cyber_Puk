import config as cfg

class World:
    def __init__(self):
        self.mod = cfg.DARK_MOD

        self.enemies = []
        self.bullets = []
        self.grenades = []
        self.effects = []
        self.walls = []
        self.items = []
        self.pings = []
        self.rooms = []

        self.core_activated = False
        self.boss_spawned = False
        self.start_room = None

        self.matrix = []