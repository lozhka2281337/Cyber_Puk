import pygame

from .weapon import Weapon
from projectile.bullet import Bullet

class Gun(Weapon):
    def __init__(self, name, damage, radius, clip, shot_delay, b_speed, b_color, spread=0, count=1, b_range=None):
        super().__init__(name, damage, radius, clip, shot_delay)
        
        self.b_speed = b_speed    
        self.b_color = b_color   
        self.spread = spread      
        self.count = count        
        self.b_range = b_range   

    def shot(self, player_pos, camera_x: float, camera_y: float, world) -> None:
        if not self._can_shoot():
            return 

        self._mark_shot()

        target = self._get_target_world_pos(camera_x, camera_y)
        start = self._get_player_center(player_pos)

        for i in range(self.count):
            angle = 0
            if self.count > 1:
                angle = (i - (self.count - 1) / 2) * self.spread

            b = Bullet(start.x, start.y, target.x, target.y, 
                       self.b_speed, self.b_color, self.damage, angle, self.b_range, True)
    
            world.bullets.append(b) 
