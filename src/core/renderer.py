import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, BLUE_WALL, MAP_WIDTH, MAP_HEIGHT

class Renderer:
    def __init__(self, screen, player, world):
        self.screen = screen
        self.player = player

        self.walls = world.walls
        self.bullets = world.bullets
        self.effects = world.effects
        self.grenades = world.grenades
        self.enemies = world.enemies

        self.FONT = pygame.font.SysFont("Arial", 32, bold=True)
        self.map_surface = pygame.Surface((MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE), pygame.SRCALPHA)

        self.init_map_surface()

    def init_map_surface(self):
        surface_width = MAP_WIDTH * TILE_SIZE
        surface_height = MAP_HEIGHT * TILE_SIZE

        # временная сетка
        for x in range(0, surface_width, TILE_SIZE):
            pygame.draw.line(self.map_surface, (100, 50, 150), (x, 0), (x, surface_height))
        for y in range(0, surface_height, TILE_SIZE):
            pygame.draw.line(self.map_surface, (100, 50, 150), (0, y), (surface_width, y))

        """ стены """
        for wall in self.walls:
            pygame.draw.rect(self.map_surface, BLUE_WALL, wall)

    def draw_hp(self):
        pygame.draw.rect(self.screen, (50, 50, 50), (10, 10, 180, 50))

        health_text = self.FONT.render(f"HP: {self.player.hp}", True, (255, 0, 0))
        self.screen.blit(health_text, (20, 15))

        if self.player.hp <= 1:
            pygame.draw.rect(self.screen, (255, 0, 0), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 5)

    def draw_death_screen(self):
        self.screen.fill((0, 0, 0))

        death_msg = self.FONT.render("GAME OVER", True, (255, 255, 255))
        self.screen.blit(death_msg, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2))
        pygame.display.flip()

        pygame.time.wait(3000)

    def draw_weapon_hud(self):
        start_x = SCREEN_WIDTH - 220
        start_y = SCREEN_HEIGHT - 80
        
        for i in range(len(self.player.inventory.weapons)):
            weapon = self.player.inventory.weapons[i]
            is_active = (i == self.player.inventory.current_idx)  
            offset_y = (i - self.player.inventory.current_idx) * -35
            w_color = getattr(weapon, 'b_color', getattr(weapon, 'color', (255, 255, 255)))

            if is_active:
                text_surf = self.FONT.render(f"> {weapon.name}", True, w_color)
            else:
                text_surf = self.FONT.render(weapon.name, True, (120, 120, 120))
                text_surf.set_alpha(150)          
            self.screen.blit(text_surf, (start_x, start_y + offset_y))

    def draw_weapon(self, camera_x, camera_y):       
        weapon = self.player.inventory.get_current()
        if hasattr(weapon, 'draw'):
            weapon.draw(self.screen, camera_x, camera_y, self.player.rect, self.walls)

    def draw(self, camera_x, camera_y):
        """ карта """
        self.screen.fill("purple")
        self.screen.blit(self.map_surface, (-camera_x, -camera_y))

        """ ентити """
        self.player.draw(self.screen, camera_x, camera_y)
        
        """ атака оружия игрока """
        self.draw_weapon(camera_x, camera_y)

        for bullet in self.bullets: 
            bullet.draw(self.screen, camera_x, camera_y)
        
        for grenade in self.grenades:
            grenade.draw(self.screen, camera_x, camera_y)

        for effect in self.effects:
            effect.draw(self.screen, camera_x, camera_y)

        for enemy in self.enemies:
            enemy.draw(self.screen, camera_x, camera_y)
    
        """ интерфейс """
        self.draw_hp()
        self.draw_weapon_hud() 

        pygame.display.flip()