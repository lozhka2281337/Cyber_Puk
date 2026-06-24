import pygame
import math

import config as cfg

class PingWave:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = cfg.PING_START_RADIUS
        self.max_radius = cfg.PING_MAX_RADIUS
        self.speed = cfg.PING_SPEED

    def update(self, world, player, dt):
        self.x = player.pos.x
        self.y = player.pos.y

        self.radius += self.speed * dt 
        if self.radius >= self.max_radius:
            world.pings.remove(self)

        # Проверяем, задела ли волна врагов
        for enemy in world.enemies:
            dx = enemy.rect.centerx - self.x
            dy = enemy.rect.centery - self.y
            distance = math.hypot(dx, dy)

            if distance <= self.radius and distance >= self.radius - self.speed * 2:
                enemy.visible_timer = cfg.ENEMY_VISIBLE_TIME

    def draw(self, surface: pygame.Surface, cam_x, cam_y):
        # Вычисляем прозрачность 
        alpha = max(0, int(255 * (1 - self.radius / self.max_radius)))
        
        cur_x = int(self.x - cam_x)
        cur_y = int(self.y - cam_y)

        pygame.draw.circle(surface, (*cfg.PING_COLOR, alpha), (cur_x, cur_y), int(self.radius), 2)
