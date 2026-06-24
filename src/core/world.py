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

    def clear_map(self):
        self.matrix.clear()
        self.enemies.clear()
        self.bullets.clear()
        self.grenades.clear()
        self.effects.clear()
        self.walls.clear()
        self.items.clear()
        self.pings.clear()
        self.rooms.clear()