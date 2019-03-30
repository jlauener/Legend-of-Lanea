import upygame

ENTITY_BUSH = 0
ENTITY_DOOR = 1
ENTITY_SPIKE = 3
ENTITY_BARRIER = 4
ENTITY_SWITCH = 5
ENTITY_SLIME = 50
ENTITY_SLIME_STRONG = 51
ENTITY_KEY = 100
ENTITY_SWORD = 101
ENTITY_POTION = 102

TILE_ENTITY_1 = 0x1
TILE_ENTITY_2 = 0x2
# 0x3 cliff
# 0x4 stalk
# 0x5 tree
# 0x6 custom_ground
# 0x7 wall
# 0x8 water
TILE_GROUND = 0x9
# 0xA custom_solid
TILE_GRASS = 0xB
TILE_ENTITY_3 = 0xC
TILE_ENTITY_4 = 0xD
TILE_ENTITY_5 = 0xE
TILE_ENTITY_6 = 0xF

class MapData:
    def __init__(self, tiles):
        self.tiles = tiles
        self.signposts = []
        self.wall = None
        #self.entity_1 = None
        #self.entity_1_tid = TILE_GRASS
        #self.entity_2 = None
        #self.entity_2_tid = TILE_GRASS
        #self.entity_3 = None
        #self.entity_3_tid = TILE_GRASS
        #self.entity_4 = None
        #self.entity_4_tid = TILE_GRASS
        #self.entity_5 = None
        #self.entity_5_tid = TILE_GRASS
        #self.entity_6 = None
        #self.entity_6_tid = TILE_GRASS
        self.custom_ground = None
        self.custom_solid = None
    
    def add_signpost(self, x, y, text):
        self.signposts.append({'x': x, 'y': y, 'text': text})
        
    def reset(self):
        self.collected_list = []
        
    def remove_collectible_at(self, x, y):
        self.collected_list.append(y * 32 + x) # Store index instead of x,y to gain some RAM
    
    def is_collected_at(self, x, y):
        index = y * 32 + x
        for c in self.collected_list:
            if c == index:
                return True
        return False
        
class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.maps = [None] * width * height
        self.intro_text = None
        self.text_sword = None
        self.text_key = None
        self.text_potion = None

    def reset(self):
        for ix in range(0, self.width):
            for iy in range(0, self.height):
                if self.get_map_at(ix, iy): self.get_map_at(ix, iy).reset()

    def set_map_at(self, x, y, map_data):
        self.maps[y * self.width + x] = map_data
        map_data.x = x
        map_data.y = y
        
    def get_map_at(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None
        return self.maps[y * self.width + x]
        
class EntityData:
    def __init__(self, hitbox_x, hitbox_y, hitbox_width, hitbox_height):
        self.hitbox = upygame.Rect(hitbox_x, hitbox_y, hitbox_width, hitbox_height)