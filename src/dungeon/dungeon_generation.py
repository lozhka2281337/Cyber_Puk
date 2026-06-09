import random
import pygame

import config as cfg


""" генерация подземелья через случайное блуждание """

class DungeonGeneration:
    def __init__(self, world, n=4000):
        self.n = n
        self.walls = world.walls

        self.dungeon_map = [[1 for _ in range(cfg.MAP_WIDTH)] for _ in range(cfg.MAP_HEIGHT)]
        self.directions = [[0, 1], [1, 0], [-1, 0], [0, -1]]
        
        self._generate_dungeon()

    def _generate_dungeon(self):
        x = random.randint(1, cfg.MAP_WIDTH-2)
        y = random.randint(1, cfg.MAP_HEIGHT-2)

        steps_made = 0
        while steps_made < self.n:
            dx, dy = random.choice(self.directions)
            
            if 1 <= x + dx < cfg.MAP_WIDTH - 1 and 1 <= y + dy < cfg.MAP_HEIGHT - 1:
                x += dx
                y += dy

                if self.dungeon_map[y][x] == 1: 
                    self.dungeon_map[y][x] = 0
                    steps_made += 1

        self._create_walls()

    def _create_walls(self):
        for y in range(cfg.MAP_HEIGHT):
            for x in range(cfg.MAP_WIDTH):
                if self.dungeon_map[y][x] == 1:
                    rect = pygame.Rect(x * cfg.TILE_SIZE, y * cfg.TILE_SIZE, cfg.TILE_SIZE, cfg.TILE_SIZE)
                    self.walls.append(rect)
            
    def get_start_coord(self):
        for y in range(cfg.MAP_HEIGHT):
            for x in range(cfg.MAP_WIDTH):
                if self.dungeon_map[y][x] == 0:
                    return x * cfg.TILE_SIZE, y * cfg.TILE_SIZE
                    
        return cfg.TILE_SIZE, cfg.TILE_SIZE

    def get_random_floor_coords(self, count):
        floors = []
        
        for y in range(cfg.MAP_HEIGHT):
            for x in range(cfg.MAP_WIDTH):
                if self.dungeon_map[y][x] == 0:
                    floors.append((x * cfg.TILE_SIZE, y * cfg.TILE_SIZE))
        
        if len(floors) < count:
            return floors
        return random.sample(floors, count)