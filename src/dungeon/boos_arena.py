import pygame

import config as cfg


class BossArena:
    def __init__(self, world):  
        self.world = world 

    def create_arena(self):
        self.world.clear_map()

        self.world.matrix = [[0 for _ in range(25)] for _ in range(20)]

        arena_w = 25 * cfg.TILE_SIZE 
        arena_h = 20 * cfg.TILE_SIZE 

        for x in range(0, arena_w, cfg.TILE_SIZE):
            self.world.walls.append(pygame.Rect(x, 0, cfg.TILE_SIZE, cfg.TILE_SIZE))
            self.world.walls.append(pygame.Rect(x, arena_h - cfg.TILE_SIZE, cfg.TILE_SIZE, cfg.TILE_SIZE))
        
        for y in range(0, arena_h, cfg.TILE_SIZE):
            self.world.walls.append(pygame.Rect(0, y, cfg.TILE_SIZE, cfg.TILE_SIZE))
            self.world.walls.append(pygame.Rect(arena_w - cfg.TILE_SIZE, y, cfg.TILE_SIZE, cfg.TILE_SIZE))

        columns_coords = [(200, 180), (540, 180), (200, 400), (540, 400)]
        for cx, cy in columns_coords:
            rect = pygame.Rect(cx, cy, cfg.TILE_SIZE * 2, cfg.TILE_SIZE * 2)
            self.world.walls.append(rect)
            
            tx, ty = cx // cfg.TILE_SIZE, cy // cfg.TILE_SIZE
            self.world.matrix[ty][tx] = 1
            self.world.matrix[ty+1][tx] = 1
            self.world.matrix[ty][tx+1] = 1
            self.world.matrix[ty+1][tx+1] = 1