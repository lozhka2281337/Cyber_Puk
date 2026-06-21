import pygame
import math

from .weapon import Weapon
from combat.damage import DamageSource, DamageType

class Melee(Weapon):
    def __init__(self, name, damage, radius, clip, shot_delay, reach, arc_degrees, color):
        super().__init__(name, damage, radius, clip, shot_delay)
        self.reach = reach
        self.arc_degrees = arc_degrees
        self.color = color
        self.is_swinging = False
        self.swing_duration = 200
        self.swing_timer = 0
        self.locked_angle = 0
        self.hit_enemies = []

    def shot(self, player_pos, camera_x: float, camera_y: float, world) -> None:
        if self.is_swinging or not self._can_shoot():
            return

        self._mark_shot()
        self.is_swinging = True
        self.swing_timer = pygame.time.get_ticks() + self.swing_duration
        self.hit_enemies = []

        target_world = self._get_target_world_pos(camera_x, camera_y)
        start_center = self._get_player_center(player_pos)

        dx = target_world.x - start_center.x
        dy = target_world.y - start_center.y
        self.locked_angle = math.degrees(math.atan2(dy, dx))

    def update(self):
        if self.is_swinging and pygame.time.get_ticks() > self.swing_timer:
            self.is_swinging = False

    def process_damage(self, enemies, player_rect, walls):
        if self.is_swinging:
            start_pos = pygame.math.Vector2(player_rect.center)

            for enemy in enemies[:]:
                if enemy in self.hit_enemies:
                    continue

                enemy_pos = pygame.math.Vector2(enemy.rect.center)
                dist = start_pos.distance_to(enemy_pos)

                if dist <= self.reach + 16:
                    dx = enemy_pos.x - start_pos.x
                    dy = enemy_pos.y - start_pos.y

                    angle_to_enemy = math.degrees(math.atan2(dy, dx))
                    angle_diff = (angle_to_enemy - self.locked_angle + 180) % 360 - 180

                    if abs(angle_diff) <= self.arc_degrees / 2:
                        enemy.get_damage(150, damage_type=DamageType.MELEE, source=DamageSource.PLAYER)

                        push_dir = enemy_pos - start_pos
                        if push_dir.magnitude() > 0:
                            enemy.knockback += push_dir.normalize() * 1200

                        self.hit_enemies.append(enemy)

    def draw(self, surface, camera_x, camera_y, player_rect, walls):
        if not self.is_swinging:
            return

        start_p = (player_rect.centerx - camera_x, player_rect.centery - camera_y)

        time_left = self.swing_timer - pygame.time.get_ticks()
        alpha = max(0, int(255 * (time_left / self.swing_duration)))

        if alpha > 0:
            from config import SCREEN_WIDTH, SCREEN_HEIGHT
            swing_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

            points = [start_p]
            start_angle = math.radians(self.locked_angle - self.arc_degrees / 2)
            end_angle = math.radians(self.locked_angle + self.arc_degrees / 2)

            steps = 10
            for i in range(steps + 1):
                angle = start_angle + (end_angle - start_angle) * (i / steps)
                x = start_p[0] + math.cos(angle) * self.reach
                y = start_p[1] + math.sin(angle) * self.reach
                points.append((x, y))

            pygame.draw.polygon(swing_surf, (*self.color, alpha // 2), points)
            pygame.draw.polygon(swing_surf, (*self.color, alpha), points, 2)

            surface.blit(swing_surf, (0, 0))