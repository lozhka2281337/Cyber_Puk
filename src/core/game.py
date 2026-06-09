import pygame

from dungeon.dungeon_generation import DungeonGeneration as dg
from dungeon.BSP.BSP_generation import BSPGeneration as BSP

from entity.enemy_type import Swarm, Tank, Shooter
from entity.player import Player

from core.world import World
from core.renderer import Renderer
from core.handler import Handler
from core.camera import Camera 

import config as cfg

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Roguelike Prototype")

        self.screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
        self.FONT = pygame.font.SysFont("Arial", 32, bold = True)
        self.clock = pygame.time.Clock()

        self.new_game()

    def new_game(self):
        self.world = World()
        self.dungeon_generator = BSP(self.world)
        self.dungeon_generator.generate_dungeon()

        player_x, player_y = self.dungeon_generator.get_start_coord()

        self.player = Player(player_x, player_y)
        self.renderer = Renderer(self.screen, self.player, self.world)
        self.handler = Handler(self.player, self.world)
        self.camera = Camera(cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT)
        
        self.spawn_enemies(player_x, player_y)
        self.running = True

    def spawn_enemies(self, player_x, player_y):
        safe_spots = self.dungeon_generator.get_random_floor_coords(5)
        
        for i, (spot_x, spot_y) in enumerate(safe_spots):
            dist_x = abs(spot_x - player_x)
            dist_y = abs(spot_y - player_y)
            
            if dist_x > 300 or dist_y > 300:
                spawn_x = spot_x + (cfg.TILE_SIZE - cfg.ENEMY_SIZE) // 2
                spawn_y = spot_y + (cfg.TILE_SIZE - cfg.ENEMY_SIZE) // 2
                
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
        self.player.update(dt, self.world)

        for bullet in self.world.bullets[:]:
            bullet.update(self.world, self.player, dt)

        for grenade in self.world.grenades[:]:
            grenade.update(self.world, self.camera, dt)
  
        for effect in self.world.effects[:]:
            effect.update(self.world.effects, dt)

        for enemy in self.world.enemies[:]:
            enemy.update(self.world, self.player, dt)

        for ping in self.world.pings[:]:
            ping.update(self.world, self.player, dt)

        self.player.process_weapon_damage(self.world.enemies, self.world.walls)
        self.world.enemies[:] = [enemy for enemy in self.world.enemies if enemy.hp > 0]
        
        if self.player.hp <= 0:
            self.death_player()

    def draw(self, cam_x, cam_y, dt):
        current_weapon = self.player.inventory.get_current()
        if hasattr(current_weapon, 'is_firing') and current_weapon.is_firing:
            self.camera.add_shake(3.0) 

        self.renderer.draw(cam_x, cam_y)

    """ главная функция """

    def run(self):
        while self.running:
            dt = min(0.05, self.clock.tick(cfg.FPS) / 1000.0)

            cam_x, cam_y = self.camera.get_offset(self.player.rect, dt)
            
            self.handler.process_events(self, cam_x, cam_y)
            self.update(dt)
            self.draw(cam_x, cam_y, dt)