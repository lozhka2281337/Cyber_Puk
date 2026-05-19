import pygame
import random

""" Генерация коридоров и комнат через BSP-дерево """

MIN_LEAF_SIZE = 65
MAX_LEAF_SIZE = 200
MIN_ROOM_SIZE = 30
MAX_ROOM_SIZE = 200

HALL_WIDTH = 10

PARTIES_RELATIONSHIP = 1.25
SPLIT_BIG_LEAF_RELATIONSHIP = 0.25
MAP_WIDTH = 320
MAP_HEIGHT = 240
TILE_SIZE = 4


class Leaf:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.left_child = None
        self.right_child = None
        self.room = None
        self.halls = []

    def split(self) -> bool:
        if self.left_child is not None or self.right_child is not None:
            return False
        
        horizontal_split = random.random() > 0.5
        if self.width / self.height > PARTIES_RELATIONSHIP:
            horizontal_split = False
        elif self.height / self.width >= PARTIES_RELATIONSHIP:
            horizontal_split = True

        mx = self.width - MIN_LEAF_SIZE
        if horizontal_split: mx = self.height - MIN_LEAF_SIZE

        if mx < MIN_LEAF_SIZE: 
            return False

        spliter = random.randint(MIN_LEAF_SIZE, mx)

        if horizontal_split:
            self.left_child = Leaf(self.x, self.y, self.width, spliter)
            self.right_child = Leaf(self.x, self.y + spliter, self.width, self.height - spliter)
        else:
            self.left_child = Leaf(self.x, self.y, spliter, self.height)
            self.right_child = Leaf(self.x + spliter, self.y, self.width - spliter, self.height)

        return True
    
    def create_rooms(self):
        if self.left_child is not None or self.right_child is not None:
            if self.left_child is not None:
                self.left_child.create_rooms()
            
            if self.right_child is not None:
                self.right_child.create_rooms()

            if self.right_child is not None and self.left_child is not None:
                self.halls = self.create_hall(self.left_child.get_room(), self.right_child.get_room())
        else:
            # создаем комнату
            room_width = random.randint(MIN_ROOM_SIZE, max(MIN_ROOM_SIZE, self.width - 2))
            room_height = random.randint(MIN_ROOM_SIZE, max(MIN_ROOM_SIZE, self.height - 2))

            room_x = random.randint(1 , max(1, self.width - room_width - 1))
            room_y = random.randint(1, max(1, self.height - room_height - 1))

            self.room = pygame.Rect((self.x + room_x) * TILE_SIZE, (self.y + room_y) * TILE_SIZE, room_width * TILE_SIZE, room_height * TILE_SIZE)
    
    def get_room(self):
        if self.room is not None:
            return self.room
        
        l_room, r_room = None, None
        
        if self.left_child is not None:  l_room = self.left_child.get_room()
        if self.right_child is not None: r_room = self.right_child.get_room()

        if l_room is None and r_room is None: return None
        elif r_room is None:                  return l_room
        elif l_room is None:                  return r_room
        elif random.random() > 0.5:           return l_room
        return r_room
    
    def create_hall(self, l, r):
        halls = []

        p1_x = (l.left // TILE_SIZE + l.right // TILE_SIZE) // 2
        p1_y = (l.top // TILE_SIZE + l.bottom // TILE_SIZE) // 2

        p2_x = (r.left // TILE_SIZE + r.right // TILE_SIZE) // 2
        p2_y = (r.top // TILE_SIZE + r.bottom // TILE_SIZE) // 2

        # Сначала горизонтально, затем вертикально
        x = min(p1_x, p2_x)
        width = abs(p2_x - p1_x) + HALL_WIDTH
        halls.append(pygame.Rect(x * TILE_SIZE, p1_y * TILE_SIZE, width * TILE_SIZE, HALL_WIDTH * TILE_SIZE))

        y = min(p1_y, p2_y)
        height = abs(p2_y - p1_y) + HALL_WIDTH
        halls.append(pygame.Rect(p2_x * TILE_SIZE, y * TILE_SIZE, HALL_WIDTH * TILE_SIZE, height * TILE_SIZE))
        
        return halls


def generate_leafs() -> list:
    leafs = []

    root = Leaf(0, 0, MAP_WIDTH, MAP_HEIGHT)
    leafs.append(root)

    runSplit = True
    while (runSplit):
        runSplit = False

        for l in leafs:
            if l.left_child != None or l.right_child != None: continue

            if l.width > MAX_LEAF_SIZE or l.height > MAX_LEAF_SIZE \
                or random.random() > SPLIT_BIG_LEAF_RELATIONSHIP:
                if l.split():
                    leafs.append(l.left_child)
                    leafs.append(l.right_child)

                    runSplit = True

    root.create_rooms()

    return leafs

def get_map() -> pygame.Surface:
    surface = pygame.Surface((MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE), pygame.SRCALPHA)
    leafs = generate_leafs()

    for leaf in leafs:
        if leaf.left_child is None and leaf.right_child is None:
            rect = pygame.Rect(leaf.x * TILE_SIZE, leaf.y * TILE_SIZE, leaf.width * TILE_SIZE, leaf.height * TILE_SIZE)
            pygame.draw.rect(surface, ("black"), rect)      
            pygame.draw.rect(surface, ("gray"), rect, 5)
            pygame.draw.rect(surface, ("brown"), leaf.room)

    for leaf in leafs:
        for hall in leaf.halls:
            pygame.draw.rect(surface, ("brown"), hall)

    return surface

