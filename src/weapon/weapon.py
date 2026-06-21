import pygame


class Weapon:
    def __init__(self, name, damage, radius, clip, shot_delay):
        self.name = name          
        self.damage = damage
        self.radius = radius
        self.clip = clip     
        self.shot_delay = shot_delay
        self.last_shot_time = 0

    def _can_shoot(self) -> bool:
        return pygame.time.get_ticks() - self.last_shot_time >= self.shot_delay

    def _mark_shot(self) -> None:
        self.last_shot_time = pygame.time.get_ticks()

    def _get_player_center(self, player_pos) -> pygame.math.Vector2:
        return pygame.math.Vector2(player_pos.x + 16, player_pos.y + 16)

    def _get_target_world_pos(self, camera_x: float, camera_y: float) -> pygame.math.Vector2:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        return pygame.math.Vector2(mouse_x + camera_x, mouse_y + camera_y)

    def shot(self, player_pos, camera_x: float, camera_y: float, world) -> None:
        raise NotImplementedError

    def update(self):
        return None

    def process_damage(self, enemies, player_rect, walls):
        return None

    def draw(self, surface, camera_x, camera_y, player_rect, walls):
        return None
