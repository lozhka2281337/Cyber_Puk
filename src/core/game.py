import pygame
import random 

from entity.enemy_type import Swarm, Tank, Shooter
from entity.player import Player
from entity.weapon import LaserWeapon 
from dungeon.dungeon_generation import DungeonGeneration as dg

from core.world import World
from core.renderer import Renderer
from core.handler import Handler

from config import (SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT, 
                    SPAWN_ENEMY_EVENT, SPAWN_ENEMY_TIME, 
                    FPS, SHOT_DELAY, BLUE_WALL, TILE_SIZE, ENEMY_SIZE)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Roguelike Prototype")

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.FONT = pygame.font.SysFont("Arial", 32, bold = True)

        self.clock = pygame.time.Clock()

        self.new_game()

    def new_game(self):
        self.world = World()

        self.dungeon_generator = dg(self.world)
        player_x, player_y = self.dungeon_generator.get_start_coord()

        self.player = Player(player_x, player_y)
        self.renderer = Renderer(self.screen, self.player, self.world)
        self.handler = Handler(self.player, self.world)

        self.running = True
        self.shake_intensity = 0 

        self.spawn_enemies(player_x, player_y)

    def spawn_enemies(self, player_x, player_y):
        # УМНЫЙ СПАВН ВРАГОВ
        safe_spots = self.dungeon_generator.get_random_floor_coords(20)
        
        for i, (spot_x, spot_y) in enumerate(safe_spots):
            dist_x = abs(spot_x - player_x)
            dist_y = abs(spot_y - player_y)
            
            if dist_x > 300 or dist_y > 300:
                spawn_x = spot_x + (TILE_SIZE - ENEMY_SIZE) // 2
                spawn_y = spot_y + (TILE_SIZE - ENEMY_SIZE) // 2
                
                # РАСПРЕДЕЛЕНИЕ ТИПОВ ВРАГОВ
                roll = i % 4
                if roll == 0:
                    self.world.enemies.append(Tank(spawn_x, spawn_y))
                elif roll == 1:
                    self.world.enemies.append(Shooter(spawn_x, spawn_y)) 
                else:
                    self.world.enemies.append(Swarm(spawn_x, spawn_y))

    def death_player(self):
        self.renderer.draw_death_screen()
        self.new_game()

    def update(self, dt: float):
        self.player.update(dt, self.world.walls)

        for weapon in self.player.inventory:
            weapon.update()

        for bullet in self.world.bullets:
            bullet.update(dt)

        for grenade in self.world.grenades:
            grenade.update(dt)

        for effect in self.world.effects:
            effect.update(dt)

        for enemy in self.world.enemies:
            enemy.update(dt, self.player, self.world)

        self.handler.process_elements(self)
        self.handler.process_player_damage(self)
        self.player.process_weapon_damage(self.world.enemies, self.world.walls)

    def draw(self, dt):
        # СИСТЕМА ТРЯСКИ ЭКРАНА (SCREEN SHAKE) 
        if self.shake_intensity > 0:
            self.shake_intensity -= 50 * dt 
            if self.shake_intensity < 0: self.shake_intensity = 0

        current_weapon = self.player.inventory[self.player.current_weapon_idx]
        if hasattr(current_weapon, 'is_firing') and current_weapon.is_firing:
            self.shake_intensity = max(self.shake_intensity, 3.0) 

        final_cam_x = self.player.rect.x + 16 - SCREEN_WIDTH / 2
        final_cam_y = self.player.rect.y + 16 - SCREEN_HEIGHT / 2

        if self.shake_intensity > 0:
            final_cam_x += random.uniform(-self.shake_intensity, self.shake_intensity)
            final_cam_y += random.uniform(-self.shake_intensity, self.shake_intensity)

        draw_cam_x = int(final_cam_x)
        draw_cam_y = int(final_cam_y)
        
        self.renderer.draw(draw_cam_x, draw_cam_y)

    """ главная функция """

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  
            
            if dt > 0.05: 
                dt = 0.05

            base_cam_x = int(self.player.rect.x + 16 - SCREEN_WIDTH / 2)
            base_cam_y = int(self.player.rect.y + 16 - SCREEN_HEIGHT / 2)
            
            self.handler.process_events(self, base_cam_x, base_cam_y)
            self.update(dt)
            self.draw(dt)
            