import pygame

from dungeon.dungeon_generation import DungeonGeneration as dg
from dungeon.BSP.BSP_generation import BSPGeneration as BSP
from entity.player import Player
from core.world import World
from core.renderer import Renderer
from core.handler import Handler
from core.camera import Camera 
from core.spawner import Spawner
from config import (SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT, 
                    FPS, TILE_SIZE, ENEMY_SIZE, PLAYER_HP) 

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
        self.dungeon_generator = BSP(self.world)
        self.dungeon_generator.generate_dungeon()

        player_x, player_y = self.dungeon_generator.get_start_coord()

        self.player = Player(player_x, player_y)
        self.renderer = Renderer(self.screen, self.player, self.world)
        self.handler = Handler(self.player, self.world)
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)     
        self.spawner = Spawner(self.world, self.dungeon_generator, self.player)
        self.spawner.spawn_initial()         
        self.running = True

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
            enemy.update(dt, self.player, self.world)

        self.player.process_weapon_damage(self.world.enemies, self.world.walls)
        self.world.enemies[:] = [enemy for enemy in self.world.enemies if enemy.hp > 0]
        
        for item in self.world.items[:]:
            if self.player.rect.colliderect(item.rect):
                if self.player.hp < PLAYER_HP: 
                    self.player.hp += 1
                    self.world.items.remove(item)

        if self.player.hp <= 0:
            self.death_player()

    def draw(self, dt):
        current_weapon = self.player.inventory.get_current()
        if hasattr(current_weapon, 'is_firing') and current_weapon.is_firing:
            self.camera.add_shake(3.0) 

        cam_x, cam_y = self.camera.get_offset(self.player.rect, dt)
        
        self.renderer.draw(cam_x, cam_y)

    def run(self):
        while self.running:
            dt = min(0.05, self.clock.tick(FPS) / 1000.0)

            cam_x, cam_y = self.camera.get_offset(self.player.rect, dt)
            
            self.handler.process_events(self, cam_x, cam_y)
            self.update(dt)
            self.draw(dt)