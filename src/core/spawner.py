import random
import pygame 
from config import TILE_SIZE, ENEMY_SIZE, INITIAL_GANGS_COUNT, MAP_WIDTH, MAP_HEIGHT
from entity.enemy_type import Swarm, Tank, Shooter
from entity.items import HealthPack 

class Spawner:
    def __init__(self, world, dungeon_generator, player):
        self.world = world
        self.dungeon_generator = dungeon_generator
        self.player = player

        # Шаблоны банд (баланс силы: примерно 4-5 очков на комнату)
        # Swarm = 1, Shooter = 2, Tank = 3
        self.gang_templates = [
            ["tank", "swarm", "swarm"],         # Вышибала и две шестерки (3+1+1 = 5)
            ["shooter", "swarm", "swarm"],      # Снайпер под прикрытием (2+1+1 = 4)
            ["tank", "shooter"],                # Элитный дуэт (3+2 = 5)
            ["swarm", "swarm", "swarm", "swarm"]# Зерг-раш (1+1+1+1 = 4)
        ]

    # Усиленная проверка: ищем широкое место 5х5 тайлов (чтобы влезла вся банда)
    def _is_in_room(self, spot_x, spot_y) -> bool:
        grid_x = int(spot_x // TILE_SIZE)
        grid_y = int(spot_y // TILE_SIZE)
        matrix = self.world.matrix
        
        # Проверяем радиус 2 тайла во все стороны от центра
        for dy in [-2, -1, 0, 1, 2]:
            for dx in [-2, -1, 0, 1, 2]:
                check_x, check_y = grid_x + dx, grid_y + dy
                if 0 <= check_x < MAP_WIDTH and 0 <= check_y < MAP_HEIGHT:
                    if matrix[check_y][check_x] != 0: # Если рядом есть стена - отмена
                        return False
        return True

    def spawn_initial(self):
        # 1. СПАВН БАНД
        # Берем кучу случайных точек с запасом
        raw_spots = self.dungeon_generator.get_random_floor_coords(300)
        
        # Фильтруем: оставляем только "широкие" центры комнат
        room_spots = [spot for spot in raw_spots if self._is_in_room(spot[0], spot[1])]
        
        # Перемешиваем точки, чтобы спавн был случайным по всей карте
        random.shuffle(room_spots)
        
        spawned_gangs = 0
        for spot_x, spot_y in room_spots:
            if spawned_gangs >= INITIAL_GANGS_COUNT:
                break
                
            dist = pygame.math.Vector2(spot_x, spot_y).distance_to(self.player.pos)
            
            # Спавним банды только далеко от стартовой зоны игрока
            if dist > 800:
                # Случайно выбираем тип банды из пресетов
                template = random.choice(self.gang_templates)
                
                # Смещения для расстановки врагов (центр, право, лево, низ, верх)
                offsets = [
                    (0, 0), 
                    (TILE_SIZE, 0), 
                    (-TILE_SIZE, 0), 
                    (0, TILE_SIZE), 
                    (0, -TILE_SIZE)
                ]
                
                # Расставляем врагов из шаблона вокруг центральной точки
                for i, enemy_type in enumerate(template):
                    if i < len(offsets):
                        spawn_x = spot_x + offsets[i][0] + (TILE_SIZE - ENEMY_SIZE) // 2
                        spawn_y = spot_y + offsets[i][1] + (TILE_SIZE - ENEMY_SIZE) // 2
                        
                        if enemy_type == "tank":
                            self.world.enemies.append(Tank(spawn_x, spawn_y))
                        elif enemy_type == "shooter":
                            self.world.enemies.append(Shooter(spawn_x, spawn_y))
                        elif enemy_type == "swarm":
                            self.world.enemies.append(Swarm(spawn_x, spawn_y))
                            
                spawned_gangs += 1

        # 2. СПАВН АПТЕЧЕК (Оставили как было, но в радиусе 1 тайла)
        item_spots = self.dungeon_generator.get_random_floor_coords(50)
        
        # Для аптечек достаточно маленькой проверки [-1, 1], они занимают мало места
        def is_safe_for_item(x, y):
            gx, gy = int(x // TILE_SIZE), int(y // TILE_SIZE)
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    cx, cy = gx + dx, gy + dy
                    if 0 <= cx < MAP_WIDTH and 0 <= cy < MAP_HEIGHT:
                        if self.world.matrix[cy][cx] != 0: return False
            return True

        valid_item_spots = [spot for spot in item_spots if is_safe_for_item(spot[0], spot[1])]
        
        for i, (spot_x, spot_y) in enumerate(valid_item_spots[:8]): # Раскидаем 8 аптечек
            spawn_x = spot_x + TILE_SIZE // 4 
            spawn_y = spot_y + TILE_SIZE // 4
            self.world.items.append(HealthPack(spawn_x, spawn_y))