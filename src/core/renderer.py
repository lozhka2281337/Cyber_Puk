import pygame

import config as cfg


class WorldRenderer:
    def __init__(self, screen, world, player, elevator, cyber_core):
        self.screen = screen
        self.player = player
        self.elevator = elevator
        self.cyber_core = cyber_core

        self.world = world

        self.map_surface = pygame.Surface((cfg.MAP_WIDTH * cfg.TILE_SIZE, cfg.MAP_HEIGHT * cfg.TILE_SIZE), pygame.SRCALPHA)

        floor_lvl1 = pygame.image.load("assets/FloorLvl1.png").convert_alpha()
        self.floor_lvl1 = pygame.transform.scale(floor_lvl1, (cfg.TILE_SIZE, cfg.TILE_SIZE))

        wall_lvl1 = pygame.image.load("assets/WallLvl1.png").convert_alpha()
        self.wall_lvl1 = pygame.transform.scale(wall_lvl1, (cfg.TILE_SIZE, cfg.TILE_SIZE))

        self.hp_sprite = pygame.image.load("assets/Hp.png").convert_alpha()
        self.hp_width = self.hp_sprite.get_width()

        self.init_map_surface()

    def draw_world(self, cam_x, cam_y):
        self.screen.fill(cfg.FLOOR_COLOR)
        self.screen.blit(self.map_surface, (-cam_x, -cam_y))

        self._draw_weapon(cam_x, cam_y)

        for item in self.world.items:
            item.draw(self.screen, cam_x, cam_y)

        for bullet in self.world.bullets:
            bullet.draw(self.screen, cam_x, cam_y)

        for grenade in self.world.grenades:
            grenade.draw(self.screen, cam_x, cam_y)

        self.elevator.draw(self.screen, cam_x, cam_y)
        self.cyber_core.draw(self.screen, cam_x, cam_y)
        self.player.draw(self.screen, cam_x, cam_y)

        for enemy in self.world.enemies:
            if enemy.visible_timer <= 0 or self.world.mod == cfg.NORMAL_MOD:
                enemy.draw(self.screen, cam_x, cam_y)

        for effect in self.world.effects:
            effect.draw(self.screen, cam_x, cam_y)

    def draw_interface(self):
        self._draw_hp()
        self._draw_weapon_hud()

    def draw_death_screen(self):
        self.screen.fill((0, 0, 0))

        death_msg = cfg.arial_font.render("GAME OVER", True, (255, 255, 255))
        self.screen.blit(death_msg, (cfg.SCREEN_WIDTH // 2 - 100, cfg.SCREEN_HEIGHT // 2 - 300))
        pygame.display.flip()

        pygame.time.wait(3000)

    def init_map_surface(self):
        for y in range(cfg.MAP_HEIGHT):
            for x in range(cfg.MAP_WIDTH):
                if self.world.matrix[y][x] == 0:
                    self.map_surface.blit(self.floor_lvl1, (x * cfg.TILE_SIZE, y * cfg.TILE_SIZE))

        for wall in self.world.walls:
            self.map_surface.blit(self.wall_lvl1, (wall.x, wall.y))

    def _draw_hp(self):
        margin_x = 10  
        margin_y = 10 
        spacing = 5  

        for i in range(self.player.hp):
            x = margin_x + i * (self.hp_width + spacing)
            y = margin_y
            self.screen.blit(self.hp_sprite, (x, y))

    def _draw_weapon_hud(self):
        start_x = cfg.SCREEN_WIDTH - 30
        start_y = cfg.SCREEN_HEIGHT - 40
        line_height = 40

        ticks = pygame.time.get_ticks()
        blink = (ticks // 500) % 2 == 0

        for i in range(len(self.player.inventory.weapons)):
            weapon = self.player.inventory.weapons[i]
            is_active = (i == self.player.inventory.current_idx)

            y = start_y - (i * line_height)

            if is_active:
                text = f"> {i + 1}. {weapon.name}"
                color = cfg.WHITE if blink else cfg.COLOR_NEON_BLUE
            else:
                text = f"{i + 1}. {weapon.name}"
                color = cfg.COLOR_NEON_BLUE

            text_surf = cfg.arial_font.render(text, True, color)
            x = start_x - text_surf.get_width()

            self.screen.blit(text_surf, (x, y))

    def _draw_weapon(self, cam_x, cam_y):
        weapon = self.player.inventory.get_current()
        if hasattr(weapon, 'draw'):
            weapon.draw(self.screen, cam_x, cam_y, self.player.rect, self.world.walls)

    def _draw_flash(self, surface):
        if self.flash_alpha > 0:
            flash_surf = pygame.Surface((cfg.WIDTH, cfg.HEIGHT))
            flash_surf.fill((255, 255, 255))
            flash_surf.set_alpha(self.flash_alpha)
            surface.blit(flash_surf, (0, 0))


class DarkRenderer:
    def __init__(self, screen, world, player, cyber_core):
        self.screen = screen
        self.world = world
        self.player = player
        self.cyber_core = cyber_core

        # маска для темноты
        self.darkness_mask = self._create_darkness_mask()

    def draw(self, cam_x, cam_y):
        for ping in self.world.pings:
            ping.draw(self.screen, cam_x, cam_y)

        self.screen.blit(self.darkness_mask, (0, 0))

        # рисуем врагов, которые попали под пинг
        for enemy in self.world.enemies:
            if enemy.visible_timer > 0.0:
                enemy.draw(self.screen, cam_x, cam_y)
        
        self._draw_core_interface(cam_x, cam_y)
        self._draw_ping_interface()

    def _draw_core_interface(self, cam_x, cam_y):
        # есил игрок рядом с ядром - рисуем подсказку
        if self.cyber_core.can_interact(self.player.rect):
            text_x = self.cyber_core.rect.centerx - cam_x
            text_y = self.cyber_core.rect.y - cam_y - 20
            
            hint_surf = cfg.menu_font.render("[ E ] ПОДКЛЮЧИТЬСЯ", True, (255, 255, 255))
            hint_rect = hint_surf.get_rect(center=(text_x, text_y))
            self.screen.blit(hint_surf, hint_rect)

    def _draw_ping_interface(self):
        status_text = "PING ГОТОВ [Q]"
        text_color = cfg.PING_COLOR

        if self.player.ping_timer > 0:

            status_text = f"СКАНИРОВАНИЕ... {round(self.player.ping_timer * 10 / cfg.FPS, 2)}"
            text_color = (100, 100, 100)

        self.screen.blit(cfg.none_font.render(status_text, True, text_color), (10, 60))

    def _create_darkness_mask(self, width=cfg.SCREEN_WIDTH, height=cfg.SCREEN_HEIGHT, radius=cfg.DARKNESS_RADIUS) -> pygame.Surface:
        mask = pygame.Surface((width, height), pygame.SRCALPHA)
        mask.fill((0, 0, 0, cfg.DARKNESS_DEGREE)) 

        for r in range(radius, 0, -2):
            alpha = int(cfg.DARKNESS_DEGREE * (r / radius))
            pygame.draw.circle(mask, (0, 0, 0, alpha), (width // 2, height // 2), r)
            
        return mask
    
