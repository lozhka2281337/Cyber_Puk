import random
import pygame 
from config import TILE_SIZE, ENEMY_SIZE, INITIAL_ENEMY_COUNT, MAP_WIDTH, MAP_HEIGHT
from entity.enemy_type import Swarm, Tank, Shooter
from entity.items import HealthPack 

class Spawner:
    def __init__(self, world, dungeon_generator, player):
        self.world = world
        self.dungeon_generator = dungeon_generator
        self.player = player

    def _is_in_room(self, spot_x, spot_y) -> bool:
        grid_x = int(spot_x // TILE_SIZE)
        grid_y = int(spot_y // TILE_SIZE)
        matrix = self.world.matrix
        
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                check_x, check_y = grid_x + dx, grid_y + dy
                if 0 <= check_x < MAP_WIDTH and 0 <= check_y < MAP_HEIGHT:
                    if matrix[check_y][check_x] != 0: 
                        return False
        return True

    def spawn_initial(self):
        raw_spots = self.dungeon_generator.get_random_floor_coords(INITIAL_ENEMY_COUNT * 10)
        room_spots = [spot for spot in raw_spots if self._is_in_room(spot[0], spot[1])]
        
        spawned = 0
        for spot_x, spot_y in room_spots:
            if spawned >= INITIAL_ENEMY_COUNT:
                break
                
            dist = pygame.math.Vector2(spot_x, spot_y).distance_to(self.player.pos)
            
            if dist > 700:
                spawn_x = spot_x + (TILE_SIZE - ENEMY_SIZE) // 2
                spawn_y = spot_y + (TILE_SIZE - ENEMY_SIZE) // 2
                
                roll = spawned % 4
                if roll == 0:
                    self.world.enemies.append(Tank(spawn_x, spawn_y))
                elif roll == 1:
                    self.world.enemies.append(Shooter(spawn_x, spawn_y)) 
                else:
                    self.world.enemies.append(Swarm(spawn_x, spawn_y))
                spawned += 1

        item_spots = self.dungeon_generator.get_random_floor_coords(30)
        valid_item_spots = [spot for spot in item_spots if self._is_in_room(spot[0], spot[1])]
        
        for i, (spot_x, spot_y) in enumerate(valid_item_spots[:10]):
            spawn_x = spot_x + TILE_SIZE // 4 
            spawn_y = spot_y + TILE_SIZE // 4
            self.world.items.append(HealthPack(spawn_x, spawn_y))