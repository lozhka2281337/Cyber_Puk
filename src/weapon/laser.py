import pygame
import math

from .weapon import Weapon

class Laser(Weapon):
    def __init__(self, name, damage, radius, clip, shot_delay, duration, beam_width, color, charge_time=400):
        super().__init__(name, damage, radius, clip, shot_delay)

        self.duration = duration
        self.beam_width = beam_width
        self.color = color
        self.charge_time = charge_time
        self.is_charging = False
        self.is_firing = False
        self.active_timer = 0
        self.locked_dir = pygame.math.Vector2(0, 0)

    def shot(self, player_pos, camera_x: float, camera_y: float, world) -> None:
        current_time = pygame.time.get_ticks()

        if self.is_firing or self.is_charging or current_time - self.last_shot_time < self.shot_delay:
            return

        self.last_shot_time = current_time

        self.is_charging = True
        self.active_timer = current_time + self.charge_time

        mx, my = pygame.mouse.get_pos()
        target_world = (mx + camera_x, my + camera_y)
        start_center = (player_pos.x + 16, player_pos.y + 16)
        dir_vec = pygame.math.Vector2(target_world[0] - start_center[0], target_world[1] - start_center[1])

        if dir_vec.magnitude() > 0:
            self.locked_dir = dir_vec.normalize()
        else:
            self.locked_dir = pygame.math.Vector2(1, 0)

    def update(self):
        current_time = pygame.time.get_ticks()

        if self.is_charging:
            if current_time > self.active_timer:
                self.is_charging = False
                self.is_firing = True
                self.active_timer = current_time + self.duration

        elif self.is_firing:
            if current_time > self.active_timer:
                self.is_firing = False

    def get_laser_end_pos(self, start_pos, walls):
        max_end = pygame.math.Vector2(
            start_pos[0] + self.locked_dir.x * 1500,
            start_pos[1] + self.locked_dir.y * 1500
        )
        final_point = max_end
        min_dist = 1500
        start_v = pygame.math.Vector2(start_pos)

        for wall in walls:
            intersect = wall.clipline(start_pos, max_end)
            if intersect:
                hit_point = pygame.math.Vector2(intersect[0])
                dist = start_v.distance_to(hit_point)
                if dist < min_dist:
                    min_dist = dist
                    final_point = hit_point
        return final_point

    def process_damage(self, enemies, player_rect, walls):
        if self.is_firing:
            start_pos = player_rect.center
            end_pos = self.get_laser_end_pos(start_pos, walls)

            for enemy in enemies[:]:
                if enemy.rect.clipline(start_pos, end_pos):
                    if hasattr(enemy, "apply_laser_damage"):
                        enemy.apply_laser_damage()
                    else:
                        enemy.get_damage(self.damage)

                    enemy.knockback += self.locked_dir * 30

    def draw(self, surface, camera_x, camera_y, player_rect, walls):
        if not self.is_charging and not self.is_firing:
            return

        start_p = (player_rect.centerx - camera_x, player_rect.centery - camera_y)

        if self.is_charging:
            pulse = math.sin(pygame.time.get_ticks() * 0.03) * 5
            radius = int(8 + pulse)
            pygame.draw.circle(surface, self.color, start_p, radius)
            pygame.draw.circle(surface, (255, 255, 255), start_p, max(1, radius - 4))

        elif self.is_firing:
            world_end = self.get_laser_end_pos(player_rect.center, walls)
            end_p = (world_end.x - camera_x, world_end.y - camera_y)

            pygame.draw.line(surface, self.color, start_p, end_p, self.beam_width)
            pygame.draw.line(surface, (255, 255, 255), start_p, end_p, max(1, self.beam_width // 3))

            spark_radius = int(self.beam_width * 1.5 + math.sin(pygame.time.get_ticks() * 0.05) * 3)
            pygame.draw.circle(surface, self.color, (int(end_p[0]), int(end_p[1])), spark_radius)
            pygame.draw.circle(surface, (255, 255, 255), (int(end_p[0]), int(end_p[1])), max(2, spark_radius // 2))