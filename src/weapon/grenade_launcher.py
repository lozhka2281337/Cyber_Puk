import pygame

from .weapon import Weapon
from projectile.grenade import Grenade

class GrenadeLauncher(Weapon):
    def __init__(self, name, radius, clip, shot_delay, throw_speed, blast_radius, fuse_time, max_range, damage=0):
        super().__init__(name, damage, radius, clip, shot_delay)
        self.throw_speed = throw_speed
        self.blast_radius = blast_radius
        self.fuse_time = fuse_time
        self.max_range = max_range
        self.color = (255, 100, 150)

    def shot(self, player_pos, camera_x: float, camera_y: float, world) -> None:
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time < self.shot_delay:
            return

        self.last_shot_time = current_time

        mx, my = pygame.mouse.get_pos()
        target_x, target_y = mx + camera_x, my + camera_y
        start_x, start_y = player_pos.x + 16, player_pos.y + 16

        grenade = Grenade(
            start_x,
            start_y,
            target_x,
            target_y,
            self.throw_speed,
            self.color,
            self.blast_radius,
            self.fuse_time,
            self.max_range,
            damage=self.damage,
            owner="player"
        )

        world.grenades.append(grenade)