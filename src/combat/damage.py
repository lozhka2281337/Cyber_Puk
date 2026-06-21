from enum import Enum


class DamageType(str, Enum):
    GENERIC = "generic"
    BULLET = "bullet"
    LASER = "laser"
    MELEE = "melee"
    GRENADE = "grenade"


class DamageSource(str, Enum):
    PLAYER = "player"
    BOSS = "boss"