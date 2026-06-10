import pygame
from enum import Enum, auto
from config import (ENEMY_SIZE, AGRO_DISTANCE, LOSE_AGRO_DISTANCE, WAYPOINT_TOLERANCE)

# ИИ которая решает, что делает враг
class EnemyState(Enum):
    IDLE = auto()   # Просто стоит на посту
    CHASE = auto()  # Агрится и бежит за игроком
    RETURN = auto() # Потерял игрока из виду и топает на пост

class Enemy:
    def __init__(self, x: int, y: int, hp: int, speed: int, color: tuple):
        self.pos = pygame.math.Vector2(x, y)
        self.rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
        
        self.hp = hp
        self.speed = speed
        self.color = color

        self.knockback = pygame.math.Vector2(0, 0)

        self.is_moving = False

        # Настройки ИИ 
        self.home_pos = pygame.math.Vector2(x, y)
        self.state = EnemyState.IDLE
        self.agro_distance = AGRO_DISTANCE
        self.lose_agro_distance = LOSE_AGRO_DISTANCE

        self.last_known_pos = None
        self.visible_timer = 0 # таймер для стелс режима

    def move(self, walls: list[pygame.Rect], dt: float, direction: pygame.math.Vector2) -> None:
        if direction.magnitude() > 0:
            direction = direction.normalize()

        old_pos = pygame.math.Vector2(self.pos)

        velocity_x = direction.x * self.speed + self.knockback.x
        velocity_y = direction.y * self.speed + self.knockback.y

        self.pos.x += velocity_x * dt
        self.rect.x = round(self.pos.x)

        for wall in walls:
            if self.rect.colliderect(wall):
                if velocity_x > 0: self.rect.right = wall.left
                elif velocity_x < 0: self.rect.left = wall.right
                self.pos.x = float(self.rect.x)
                self.knockback.x = 0

        self.pos.y += velocity_y * dt
        self.rect.y = round(self.pos.y)

        for wall in walls:
            if self.rect.colliderect(wall):
                if velocity_y > 0: self.rect.bottom = wall.top
                elif velocity_y < 0: self.rect.top = wall.bottom
                self.pos.y = float(self.rect.y)
                self.knockback.y = 0

        if self.knockback.magnitude() > 10:
            self.knockback = self.knockback.lerp(pygame.math.Vector2(0, 0), dt * 10)
        else:
            self.knockback.x, self.knockback.y = 0, 0

        self.is_moving = old_pos.distance_to(self.pos) > 0.01

    def get_damage(self, damage: int) -> None:
        self.hp -= damage
        if self.state in [EnemyState.IDLE, EnemyState.RETURN]:
            self.state = EnemyState.CHASE

    def check_los(self, target_rect: pygame.Rect, walls: list[pygame.Rect]) -> bool:
        line = (self.rect.center, target_rect.center)
        for wall in walls:
            if wall.clipline(line):
                return False
        return True

    # Поведение в разных ситуациях 
    def _handle_chase(self, player, world, dt: float) -> pygame.math.Vector2:
        if self.check_los(player.rect, world.walls):
            return pygame.math.Vector2(player.rect.centerx - self.rect.centerx,
                                       player.rect.centery - self.rect.centery)
        elif self.last_known_pos:
            vec_to_lkp = self.last_known_pos - self.pos
            if vec_to_lkp.magnitude() < WAYPOINT_TOLERANCE:
                self.last_known_pos = None 
                return pygame.math.Vector2(0, 0)
            return vec_to_lkp

        return pygame.math.Vector2(0, 0)

    def _handle_return(self, world, dt: float) -> pygame.math.Vector2:
        vec_to_home = self.home_pos - self.pos
        if vec_to_home.magnitude() < WAYPOINT_TOLERANCE:
            self.state = EnemyState.IDLE 
            return pygame.math.Vector2(0, 0)
        return vec_to_home

    def update(self, world, player, dt: float) -> None:
        dist_to_player = self.pos.distance_to(player.pos)
        has_los = self.check_los(player.rect, world.walls)

        if has_los:
            self.last_known_pos = pygame.math.Vector2(player.rect.center)

        if self.state in [EnemyState.IDLE, EnemyState.RETURN]:
            if dist_to_player < self.agro_distance and has_los:
                self.state = EnemyState.CHASE

        elif self.state == EnemyState.CHASE:
            if has_los:
                if dist_to_player > self.lose_agro_distance:
                    self.state = EnemyState.RETURN
                    self.last_known_pos = None
            else:
                if not self.last_known_pos:
                    self.state = EnemyState.RETURN

        direction = pygame.math.Vector2(0, 0)

        if self.state == EnemyState.CHASE:
            direction = self._handle_chase(player, world, dt)
        elif self.state == EnemyState.RETURN:
            direction = self._handle_return(world, dt)

        if self.visible_timer > 0:
            self.visible_timer -= dt

        self.move(world.walls, dt, direction)

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float) -> None:
        offset_rect = self.rect.move(-cam_x, -cam_y)
        pygame.draw.rect(surface, self.color, offset_rect)

class AnimatedEnemy(Enemy):
    def __init__(self, x: int, y: int, hp: int, speed: int, color: tuple):
        super().__init__(x, y, hp, speed, color)
        self.anim_left = None
        self.anim_right = None
        self.current_anim = None


    def update(self, world, player, dt: float) -> None:
        super().update(world, player, dt)
        
        if player.rect.centerx < self.rect.centerx:
            self.current_anim = self.anim_left
        else:
            self.current_anim = self.anim_right

        if self.is_moving:
            self.current_anim.update(dt)
        else:
            self.current_anim.current_idx = 0

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float) -> None:
        if not self.current_anim:
            super().draw(surface, cam_x, cam_y)
            return

        frame = self.current_anim.get_frame()
        screen_x = self.rect.x - cam_x
        screen_y = self.rect.y - cam_y
        center_x = screen_x + self.rect.width // 2
        center_y = screen_y + self.rect.height // 2
        frame_rect = frame.get_rect(center=(center_x, center_y))
        surface.blit(frame, frame_rect)