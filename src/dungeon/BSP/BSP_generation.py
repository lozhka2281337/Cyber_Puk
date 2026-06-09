import pygame
import random

import config as cfg

from .leaf import Leaf

""" Генерация коридоров и комнат через BSP-дерево """

class BSPGeneration:
    def __init__(self, world):
        self.world = world

        self.leafs = [] 

    def generate_dungeon(self):
        self._generate_leafs() 
        self._init_matrix()
        self._create_walls()

    def get_start_coord(self):
        for y in range(cfg.MAP_HEIGHT):
                for x in range(cfg.MAP_WIDTH):
                    if self.world.matrix[y][x] == 0:
                        return [x*cfg.TILE_SIZE, y*cfg.TILE_SIZE]

    def get_random_floor_coords(self, count):
        floors = []
        
        for y in range(cfg.MAP_HEIGHT):
            for x in range(cfg.MAP_WIDTH):
                if self.world.matrix[y][x] == 0:
                    floors.append((x * cfg.TILE_SIZE, y * cfg.TILE_SIZE))
        
        if len(floors) < count:
            return floors
        return random.sample(floors, count)

    def _generate_leafs(self):
        root = Leaf(0, 0, cfg.MAP_WIDTH, cfg.MAP_HEIGHT)
        self.leafs.append(root)

        runSplit = True
        while (runSplit):
            runSplit = False

            for l in self.leafs:
                if l.left_child != None or l.right_child != None: continue

                if (l.width > cfg.MAX_LEAF_SIZE) or (l.height > cfg.MAX_LEAF_SIZE) or (random.random() > cfg.SPLIT_BIG_LEAF_RELATIONSHIP):
                    if l.split():
                        self.leafs.append(l.left_child)
                        self.leafs.append(l.right_child)

                        runSplit = True

        root.create_rooms()

    def _init_matrix(self):
        self.world.matrix = [[1 for _ in range(cfg.MAP_WIDTH)] for _ in range(cfg.MAP_HEIGHT)]

        for leaf in self.leafs:
            if leaf.room is not None:
                x = leaf.room.x
                y = leaf.room.y

                for dy in range(leaf.room.height):
                    for dx in range(leaf.room.width):
                        nx = min(cfg.MAP_WIDTH-1, x+dx)
                        ny = min(cfg.MAP_HEIGHT-1, y+dy)

                        self.world.matrix[ny][nx] = 0
        
        for leaf in self.leafs:
            for hall in leaf.halls:
                x = hall.x
                y = hall.y

                for dy in range(hall.height):
                    for dx in range(hall.width):
                        nx = min(cfg.MAP_WIDTH-1, x+dx)
                        ny = min(cfg.MAP_HEIGHT-1, y+dy)

                        self.world.matrix[ny][nx] = 0

    def _create_walls(self):
        for y in range(cfg.MAP_HEIGHT):
            for x in range(cfg.MAP_WIDTH):
                if self.world.matrix[y][x] == 1:
                    # Проверяем, касается ли стена пола хотя бы с одной стороны
                    is_visible = False
                    for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < cfg.MAP_HEIGHT and 0 <= nx < cfg.MAP_WIDTH:
                            if self.world.matrix[ny][nx] == 0:
                                is_visible = True
                                break
                    
                    if is_visible:
                        rect = pygame.Rect(x * cfg.TILE_SIZE, y * cfg.TILE_SIZE, cfg.TILE_SIZE, cfg.TILE_SIZE)
                        self.world.walls.append(rect)



