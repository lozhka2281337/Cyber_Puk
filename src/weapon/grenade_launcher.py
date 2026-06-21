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
        if not self._can_shoot():
            return

        self._mark_shot()

        target = self._get_target_world_pos(camera_x, camera_y)
        start = self._get_player_center(player_pos)

        grenade = Grenade(
            start.x,
            start.y,
            target.x,
            target.y,
            self.throw_speed,
            self.color,
            self.blast_radius,
            self.fuse_time,
            self.max_range,
            owner="player",
            damage=self.damage
        )

        world.grenades.append(grenade)