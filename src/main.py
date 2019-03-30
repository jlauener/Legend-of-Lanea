import upygame as pygame
import urandom as random
import umachine as machine
import data
import data_type as dt
import gfx
import sfx
import gc

pygame.display.init(False)
pygame.display.set_palette_16bit([
	4195,16678,12717,19017,13092,33382,53801,29580,23545,54245,33972,27973,28185,54611,57003,57210
]);
screen = pygame.display.set_mode()

SCREEN_WIDTH = 110
SCREEN_HEIGHT = 88

#SKIP_INTRO = False
#DEBUG_SWORD = True
#WORLD_DATA = data.world

TILE_WIDTH = 16
TILE_HEIGHT = 16

MAP_WIDTH = 32
MAP_HEIGHT = 32
MAP_WIDTH_PX = MAP_WIDTH * TILE_WIDTH
MAP_HEIGHT_PX = MAP_HEIGHT * TILE_HEIGHT

DIR_NONE = -1
DIR_LEFT = 0
DIR_RIGHT = 1
DIR_UP = 2
DIR_DOWN = 3

STATE_IDLE = 0
STATE_WALK = 1
STATE_ATTACK = 2
STATE_DIE = 3
STATE_HURT = 4
STATE_COLLECT = 5
STATE_SLEEP = 6
STATE_DEAD = 7

TEXT_RECT = pygame.Rect(0, 46, 110, 42)

# Temporary rect to prevent filling up GC (most likely a bad practice...)
rect_1 = pygame.Rect(0, 0, 0, 0)
rect_2 = pygame.Rect(0, 0, 0, 0)

class Camera:
    def __init__(self, bounds):
        self.bounds = bounds
        self.x = 0
        self.y = 0
        self.look_x = 0
        self.look_y = 0
        self.shake_x = 0
        self.shake_y = 0
        self.bounce_x = 0
        self.bounce_y = 0
        
    def look_at(self, x, y):
        self.look_x = x
        self.look_y = y
        
    def shake(self, x, y):
        self.shake_x = x
        if self.shake_x < 0: self.shake_x = -self.shake_x
        
        self.shake_y = y
        if self.shake_y < 0: self.shake_y = -self.shake_y
        
    def bounce(self, x, y):
        self.bounce_x = x
        self.bounce_y = y
        
    def update(self):
        self.x = self.look_x
        self.y = self.look_y
        
        if self.shake_x > 0:
            self.x += rand_range(-self.shake_x, self.shake_x)
            self.shake_x -= 1
            
        if self.shake_y > 0:
            self.y += rand_range(-self.shake_y, self.shake_y)
            self.shake_y -= 1
            
        self.x += self.bounce_x
        if self.bounce_x > 0: self.bounce_x -= 1
        elif self.bounce_x < 0: self.bounce_x += 1
        
        self.y += self.bounce_y
        if self.bounce_y > 0: self.bounce_y -= 1
        elif self.bounce_y < 0: self.bounce_y += 1
        
        if self.x < self.bounds.x: self.x = self.bounds.x
        elif self.x > self.bounds.x + self.bounds.width - SCREEN_WIDTH:
            self.x = self.bounds.x + self.bounds.width - SCREEN_WIDTH
    
        if self.y < self.bounds.x: self.y = self.bounds.y
        elif self.y > self.bounds.y + self.bounds.height - SCREEN_HEIGHT:
            self.y = self.bounds.y + self.bounds.height - SCREEN_HEIGHT
        
camera = Camera(pygame.Rect(0, 0, MAP_WIDTH * TILE_WIDTH, MAP_HEIGHT * TILE_HEIGHT))

sound = pygame.mixer.Sound()

def draw_text_centered(x, y, text, color):
     machine.draw_text(x - len(text) * 2, y, text, color)
     
def rand_int(max):
    return random.getrandbits(16) % max
    
def rand_range(min, max):
    return min + random.getrandbits(16) % (max - min)
    
#def rand_dir():
#    rnd = rand_int(4)
#    if rnd == 0:
#        return DIR_LEFT
#    elif rnd == 1:
#        return DIR_RIGHT
#    elif rnd == 2:
#        return DIR_UP
#    else:
#        return DIR_DOWN
        
def rand_dir_xy():
    rnd = rand_int(8)
    if rnd == 0:    return -1, 0
    elif rnd == 1:  return 1, 0
    elif rnd == 2:  return 0, -1
    elif rnd == 3:  return 0, 1
    elif rnd == 4:  return -1, -1
    elif rnd == 5:  return 1, 1
    elif rnd == 6:  return 1, -1
    else:           return -1, 1
        
def get_dir_xy(dir):
    if dir == DIR_LEFT:
        return -1, 0
    elif dir == DIR_RIGHT:
        return 1, 0
    elif dir == DIR_UP:
        return 0, -1
    else:
        return 0, 1
        
def get_dir(dx, dy):
    if dx < 0: return DIR_LEFT
    elif dx > 0 : return DIR_RIGHT
    elif dy < 0: return DIR_UP
    elif dy > 0: return DIR_DOWN
    else: return DIR_NONE
        
def get_opposite_dir(dir):
    if dir == DIR_LEFT:
        return DIR_RIGHT
    elif dir == DIR_RIGHT:
        return DIR_LEFT
    elif dir == DIR_UP:
        return DIR_DOWN
    else:
        return DIR_UP

def get_tile_at(map_data, x, y):
    if x % 2 == 0:
        return (map_data[y * MAP_WIDTH // 2 + x // 2] & 0xF0) >> 4
    else:
        return map_data[y * MAP_WIDTH // 2 + x // 2] & 0x0F
    
def set_tile_at(map_data, x, y, tid):
    index = y * MAP_WIDTH // 2 + x // 2
    if x % 2 == 0:
        map_data[index] = (map_data[index] & 0x0F) | tid << 4
    else:
        map_data[index] = (map_data[index] & 0xF0) | tid

class Entity:
    def __init__(self, tile_x, tile_y, entity_data):
        self.x = tile_x * TILE_WIDTH + TILE_WIDTH // 2
        self.y = tile_y * TILE_HEIGHT + TILE_HEIGHT
        self.data = entity_data
        
    def move_by(self, dx, dy):
        
        collide = False
        if dx != 0:
            if not game.map_collide(self.x + dx, self.y, self.data.hitbox):
                self.x += dx
            else:
                collide = True
                    
        if dy != 0:
            if not game.map_collide(self.x, self.y + dy, self.data.hitbox):
                self.y +=dy
            else:
                collide = True
        
        return collide
        
    def collide_with(self, x, y, other):
        rect_1.x = x + self.data.hitbox.x
        rect_1.y = y + self.data.hitbox.y
        rect_1.width = self.data.hitbox.width
        rect_1.height = self.data.hitbox.height
        rect_2.x = other.x + other.data.hitbox.x
        rect_2.y = other.y + other.data.hitbox.y
        rect_2.width = other.data.hitbox.width
        rect_2.height = other.data.hitbox.height
        return rect_1.colliderect(rect_2)
        
    def collide_with_rect(self, rect):
        rect_2.x = self.x + self.data.hitbox.x
        rect_2.y = self.y + self.data.hitbox.y
        rect_2.width = self.data.hitbox.width
        rect_2.height = self.data.hitbox.height
        return rect.colliderect(rect_2)
        
    def draw_anim(self, x, y, anim, interval, loop):
        screen.blit(anim[self.frame_index], x - camera.x, y - camera.y)
        if not game.text: # FIXME this is a bit hackish, don't play anims while text is shown
            self.anim_counter += 1
            if self.anim_counter == interval:
                self.anim_counter = 0
                self.frame_index += 1
                if self.frame_index == len(anim):
                    if loop: self.frame_index = 0
                    else:
                        self.frame_index -=1 # Keep the last frame (FIXME?).
                        return True # Indicate a one-shot anim is finished.

class Player(Entity):
    def __init__(self, tile_x, tile_y, entity_data):
        Entity.__init__(self, tile_x, tile_y, entity_data)
        
        self.dir = DIR_DOWN
        self.state = STATE_IDLE
        self.state_counter = 0

        self.anim_counter = 0
        self.frame_index = 0
        self.immune_counter = 0
                
    def attack(self):
        attack_hitbox = self.data.attack_hitbox[self.dir]
        rect_1.x = self.x + attack_hitbox.x
        rect_1.y = self.y + attack_hitbox.y
        rect_1.width = attack_hitbox.width
        rect_1.height = attack_hitbox.height
        
         # Special case: signpost (SHOULD BE RENAMED)
        for e in game.signposts:
            if e.collide_with_rect(rect_1):
                e.activate()
                return
    
        if not game.has_sword:
            # TODO feedback?
            return
        
        self.state = STATE_ATTACK
        self.state_counter = 8
        
        damaged_enemy = False
        for e in game.enemies:
            if e.collide_with_rect(rect_1) and e.damage(1, self.dir, 10):
                damaged_enemy = True

        damaged_any = damaged_enemy
        
        for e in game.bushes:
            if e.collide_with_rect(rect_1) and e.damage(1, self.dir, 10):
                damaged_any = True
        
        if damaged_enemy:
            dx, dy = get_dir_xy(self.dir)
            camera.shake(dx * 4, dy * 4)
        
        if damaged_any:
            sound.play_sfx(sfx.attack_hit, len(sfx.attack_hit), True)
        else:
            sound.play_sfx(sfx.attack_miss, len(sfx.attack_miss), True)
        
    def damage(self, value):
        if self.immune_counter > 0: return
        if self.state == STATE_DEAD: return
    
        game.hp -= value
        if game.hp <= 0:
            self.state = STATE_DEAD
            game.hp = 0
            camera.shake(10, 10)
        else:
            self.state = STATE_HURT
            self.state_counter = 6
            self.immune_counter = 24
            camera.shake(8, 8)
            
        sound.play_sfx(sfx.hurt, len(sfx.hurt), True)
        
    def collect(self, collectible):
        if collectible.data.collectible_id == dt.ENTITY_KEY:
            game.key += 1
            if game.world.text_key: game.show_text(game.world.text_key)
            sound.play_sfx(sfx.collect, len(sfx.collect), True)
        elif collectible.data.collectible_id == dt.ENTITY_POTION:
            game.hp += 1
            if game.world.text_potion: game.show_text(game.world.text_potion)
            sound.play_sfx(sfx.heal, len(sfx.heal), True)
        elif collectible.data.collectible_id == dt.ENTITY_SWORD:
            game.has_sword = True
            self.collected_sprite = gfx.collectible_sword_collect
            if game.world.text_sword: game.show_text(game.world.text_sword)
            sound.play_sfx(sfx.collect, len(sfx.collect), True)
            
        game.current_map.remove_collectible_at(collectible.tile_x, collectible.tile_y)
        self.collected_sprite = collectible.data.sprite_collect
        self.state = STATE_COLLECT
        self.state_counter = 4
        return True
        
    def use_key(self):
        if game.key == 0: return False
        game.key -= 1
        return True
        
    def update(self):
        if self.state == STATE_DEAD: return
        if self.immune_counter > 0: self.immune_counter -= 1

        if self.state == STATE_ATTACK:
            self.state_counter -= 1
            if self.state_counter == 0:
                self.state = STATE_IDLE
                self.anim_counter = 0
                self.frame_index = 0
                
        elif self.state == STATE_COLLECT:
            self.state_counter -= 1
            if self.state_counter == 0:
                self.state = STATE_IDLE
                self.anim_counter = 0
                self.frame_index = 0

        else:
            if input_x != 0: self.move_by_and_collide(input_x, 0)
            if input_y != 0: self.move_by_and_collide(0, input_y)
                
            if self.state == STATE_HURT:
                self.state_counter -= 1
                if self.state_counter == 0:
                    self.state = STATE_IDLE
                    self.anim_counter = 0
                    self.frame_index = 0
            elif input_a:
                self.attack()
            #elif input_b:
            #    self.act()
            elif input_x < 0:
                self.dir = DIR_LEFT
                self.state = STATE_WALK
            elif input_x > 0:
                self.dir = DIR_RIGHT
                self.state = STATE_WALK
            elif input_y < 0:
                self.dir = DIR_UP
                self.state = STATE_WALK
            elif input_y > 0:
                self.dir = DIR_DOWN
                self.state = STATE_WALK
            else:
                self.state = STATE_IDLE
                self.anim_counter = 0
                self.frame_index = 0
                
    def move_by_and_collide(self, dx, dy):
        blocked = False
        for e in game.doors:
            if self.collide_with(self.x + dx, self.y + dy, e) and e.hit(self): blocked = True
        
        for e in game.bushes:
            if self.collide_with(self.x + dx, self.y + dy, e) and e.hit(self): blocked = True
            
        for e in game.signposts:
            if self.collide_with(self.x + dx, self.y + dy, e):
                self.signpost = e
                blocked = True
            
        # Check if the player goes out of the map
        if dx < 0 and self.x < 8: game.load_next_map(-1, 0)
        elif dx > 0 and self.x > MAP_WIDTH_PX - 8: game.load_next_map(1, 0)
        elif dy < 0 and self.y < 16: game.load_next_map(0, -1)
        elif dy > 0 and self.y > MAP_HEIGHT_PX - 1: game.load_next_map(0, 1)
        elif not blocked: self.move_by(dx, dy)
        
    def draw(self):
        if self.immune_counter > 0 and self.state != STATE_HURT:
            # Blink while immune.
            if (self.immune_counter // 3) % 2 == 0:
                return

        if self.state == STATE_IDLE:
            screen.blit(self.data.anim_idle[self.dir], (self.x - 8) - camera.x, (self.y - 16) - camera.y)
            
        elif self.state == STATE_WALK:
            self.draw_anim(self.x - 8, self.y - 16, self.data.anim_walk[self.dir], 8, True)
            
        elif self.state == STATE_COLLECT:
            screen.blit(gfx.player_collect, (self.x - 8) - camera.x, (self.y - 16) - camera.y)
            screen.blit(self.collected_sprite, (self.x - 9) - camera.x, (self.y - 19) - camera.y)

        elif self.state == STATE_ATTACK:
            if self.state_counter < 4:
                screen.blit(self.data.anim_idle[self.dir], (self.x - 8) - camera.x, (self.y - 16) - camera.y)
            else:
                if self.dir == DIR_UP:
                     screen.blit(gfx.item_sword[DIR_UP], (self.x + 1) - camera.x, (self.y - 19) - camera.y)
                     
                screen.blit(self.data.anim_attack[self.dir], (self.x - 8) - camera.x, (self.y - 16) - camera.y)
                
                if self.dir == DIR_LEFT:
                    screen.blit(gfx.item_sword[DIR_LEFT], (self.x - 15) - camera.x, (self.y - 9) - camera.y)
                elif self.dir == DIR_RIGHT:
                    screen.blit(gfx.item_sword[DIR_RIGHT], (self.x + 6) - camera.x, (self.y - 9) - camera.y)
                elif self.dir == DIR_DOWN:
                    screen.blit(gfx.item_sword[DIR_DOWN], (self.x - 6) - camera.x, (self.y - 3) - camera.y)
                    
        elif self.state == STATE_HURT:
            screen.blit(self.data.anim_hurt[self.dir], (self.x - 8) - camera.x, (self.y - 16) - camera.y)
            
        elif self.state == STATE_SLEEP:
            screen.blit(gfx.player_sleep, (self.x - 8) - camera.x, (self.y - 16) - camera.y)
            
        elif self.state == STATE_DEAD:
            screen.blit(gfx.player_dead, (self.x - 8) - camera.x, (self.y - 16) - camera.y)
        
class Enemy(Entity):
    def __init__(self, tile_x, tile_y, entity_data):
        Entity.__init__(self, tile_x, tile_y, entity_data)
        
        self.hp = entity_data.hp
        self.dir_x = 0
        self.dir_y = 1
        self.dir = DIR_DOWN
        self.state = STATE_IDLE
        self.state_counter = 1

        self.move_counter = 0

        self.anim_counter = 0
        self.frame_index = 0
        
    def damage(self, value, dir, knockback):
        if self.hp == 0: return False

        self.hp -= value
        if self.hp < 0: self.hp = 0
        
        self.dir_x, self.dir_y = get_dir_xy(dir)
        self.dir = get_opposite_dir(dir)
        self.state = STATE_HURT
        self.state_counter = knockback
        return True
        
    def update(self):
        dist_x = self.x - game.player.x
        if dist_x < 0: dist_x = -dist_x
        if dist_x > 60: return
        
        dist_y = self.y - game.player.y
        if dist_y < 0: dist_y = -dist_y
        if dist_y > 50: return
        
        #if dist_x + dist_y > 128: return
        
        if self.state == STATE_WALK:
            self.state_counter -= 1
            if self.state_counter == 0:
                self.state = STATE_IDLE
                self.state_counter = rand_range(self.data.idle_duration_min, self.data.idle_duration_max)
            else:
                self.move_counter += 1
                if self.move_counter == 2: # FIXME add value for that (removed to gain some RAM)
                    if self.move_by(self.dir_x, self.dir_y):
                        self.state = STATE_IDLE
                        self.state_counter = rand_range(self.data.idle_duration_min, self.data.idle_duration_max)
                    self.move_counter = 0
        elif self.state == STATE_IDLE:
            self.state_counter -= 1
            if self.state_counter == 0:
                dir_x, dir_y = rand_dir_xy()
                while dir_x == self.dir_x and dir_y == self.dir_y:
                     dir_x, dir_y = rand_dir_xy()
                     
                self.dir_x = dir_x
                self.dir_y = dir_y
                
                if self.dir_x < 0: self.dir = DIR_LEFT
                elif self.dir_x > 0: self.dir = DIR_RIGHT
                elif self.dir_y < 0: self.dir = DIR_UP
                elif self.dir_y > 0: self.dir = DIR_DOWN
                
                self.state = STATE_WALK
                self.state_counter = self.state_counter = rand_range(self.data.walk_duration_min, self.data.walk_duration_max)
                self.anim_counter = 0
                self.frame_index = 0
        elif self.state == STATE_HURT:
            self.move_by(self.dir_x * (self.state_counter // 3), self.dir_y * (self.state_counter // 3))
            self.state_counter -= 1
            if self.state_counter == 0:
                if self.hp == 0:
                    self.state = STATE_DIE
                    self.state_counter = 12
                    self.anim_counter = 0
                    self.frame_index = 0
                    
                    camera.bounce(0, 3)
                    sound.play_sfx(sfx.enemy_die, len(sfx.enemy_die), True)
                else:
                    self.state = STATE_IDLE
                    self.state_counter = 20
        elif self.state == STATE_DIE:
            self.state_counter -= 1
            if self.state_counter == 0:
                game.enemies.remove(self)
                
        if self.state == STATE_IDLE or self.state == STATE_WALK:
            if self.collide_with(self.x, self.y, game.player):
                game.player.damage(1)

    def draw(self):
        if self.state == STATE_IDLE:
            screen.blit(self.data.anim_idle[self.dir], (self.x - 8) - camera.x, (self.y - 13) - camera.y)
        elif self.state == STATE_WALK:
            self.draw_anim(self.x - 8, self.y - 13, self.data.anim_walk[self.dir], 4, True)
        elif self.state == STATE_HURT:
            if self.state_counter < 8:
                screen.blit(self.data.anim_idle[self.dir], (self.x - 8) - camera.x, (self.y - 13) - camera.y)
            else:
                screen.blit(self.data.anim_hurt[self.dir], (self.x - 8) - camera.x, (self.y - 13) - camera.y)
        elif self.state == STATE_DIE:
            self.draw_anim(self.x - 4, self.y - 9, gfx.fx_enemy_die, 3, False)

class Collectible(Entity):
    def __init__(self, tile_x, tile_y, entity_data):
        Entity.__init__(self, tile_x, tile_y, entity_data)
        self.tile_x = tile_x
        self.tile_y = tile_y
        
    def update(self):
        if self.collide_with(self.x, self.y, game.player) and game.player.collect(self):
            # TODO collect anim
            game.collectibles.remove(self)
            
    def draw(self):
         screen.blit(self.data.sprite_idle, (self.x - 5) - camera.x, (self.y - 14) - camera.y)
       
# Create a single big entity to gain RAM ...
class GenericEntity(Entity):
    def __init__(self, tile_x, tile_y, entity_data):
        Entity.__init__(self, tile_x, tile_y, entity_data)
        
        if entity_data == data.bush:
            self.alive = True
        elif entity_data == data.door:
            self.closed = True
            self.anim_counter = 0
            self.frame_index = 0
        elif entity_data == data.switch:
            self.on = False
        elif entity_data == data.barrier:
            self.switch_count = 2 # FIXME
        elif entity_data == data.spike:
            self.up = (tile_x % 2 == 0 and tile_y % 2 == 0) or (tile_x % 2 == 1 and tile_y % 2 == 1)
            if self.up: self.counter = 40
            else: self.counter = 55 # Shift start to sync the spikes: (70-40) / 2 = 15
            
    def hit(self, player):
        if self.data == data.bush:
            return self.alive
        elif self.data == data.door:
            if self.closed and player.use_key():
                self.closed = False
                sound.play_sfx(sfx.attack_miss, len(sfx.attack_miss), True)

            return self.closed
        elif self.data == data.barrier:
             return True
                
    def damage(self, value, dir, knockback):
        if self.data == data.bush:
            if not self.alive: return False
    
            self.alive = False
            self.anim_counter = 0
            self.frame_index = 0
            return True
            
    def activate(self):
        if self.data == data.switch:
            if not self.on:
                self.on = True
                game.barrier.activate() # FIXME
                sound.play_sfx(sfx.attack_miss, len(sfx.attack_miss), True)
            else:
                game.show_text([['It seems that', 'it\'s activated.']])
        elif self.data == data.barrier:
            self.switch_count -= 1
            if self.switch_count == 0: game.doors.remove(self)
        elif self.data == data.signpost:
            game.show_text(self.text)
            sound.play_sfx(sfx.select, len(sfx.select), True)

    def update(self):
        #if self.data == data.spike: # small optimization to make dungeon a bit faster...
        if self.up and self.counter > 6 and self.collide_with(self.x, self.y, game.player):
            game.player.damage(1)
        
        self.counter -= 1
        if self.counter == 0:
            self.up = not self.up
            if self.up: self.counter = 40
            else: self.counter = 70
            
    def draw(self):
        if self.data == data.bush:
            if self.alive:
                screen.blit(gfx.bush_idle, (self.x - 8) - camera.x, (self.y - 15) - camera.y)
            else:
                if self.draw_anim(self.x - 4, self.y - 13, gfx.fx_enemy_die, 3, False):
                    game.bushes.remove(self)
        elif self.data == data.door:
            if self.closed:
                screen.blit(gfx.door_closed, (self.x - 8) - camera.x, (self.y - 16) - camera.y)
            else:
                self.draw_anim(self.x - 8, self.y - 16, self.data.anim_open, 4, False)
        elif self.data == data.switch:
            if self.on:
                screen.blit(gfx.switch_on, (self.x - 7) - camera.x, (self.y - 12) - camera.y)
            else:
                screen.blit(gfx.switch_off, (self.x - 7) - camera.x, (self.y - 12) - camera.y)
        elif self.data == data.barrier:
            screen.blit(gfx.barrier_closed, (self.x - 8) - camera.x, (self.y - 16) - camera.y)
        elif self.data == data.spike:
            if self.counter < 6:
                screen.blit(gfx.spike_middle, (self.x - 7) - camera.x, (self.y - 16) - camera.y)
            elif self.up:
                screen.blit(gfx.spike_up, (self.x - 7) - camera.x, (self.y - 16) - camera.y)
            else:
                screen.blit(gfx.spike_down, (self.x - 7) - camera.x, (self.y - 16) - camera.y)
        elif self.data == data.signpost:
            screen.blit(gfx.signpost_idle, (self.x - 5) - camera.x, (self.y - 12) - camera.y)
            
''''
class Bush(Entity):
    def __init__(self, tile_x, tile_y, entity_data):
        Entity.__init__(self, tile_x, tile_y, entity_data)
        self.alive = True
        
    def hit(self, player):
        return self.alive
        
    def damage(self, value, dir, knockback):
        if not self.alive: return False
        
        self.alive = False
        self.anim_counter = 0
        self.frame_index = 0
        return True
            
    def draw(self):
        if self.alive:
            screen.blit(gfx.bush_idle, (self.x - 8) - camera.x, (self.y - 15) - camera.y)
        else:
            if self.draw_anim(self.x - 4, self.y - 13, gfx.fx_enemy_die, 3, False):
                game.bushes.remove(self)
''' 

'''
class Door(Entity):
    def __init__(self, tile_x, tile_y, entity_data):
        Entity.__init__(self, tile_x, tile_y, entity_data)
        self.closed = True
        self.anim_counter = 0
        self.frame_index = 0
        
    def hit(self, player):
        if self.closed and player.use_key():
            self.closed = False
            sound.play_sfx(sfx.attack_miss, len(sfx.attack_miss), True)

        return self.closed
        
    def draw(self):
        if self.closed:
            screen.blit(gfx.door_closed, (self.x - 8) - camera.x, (self.y - 16) - camera.y)
        else:
            self.draw_anim(self.x - 8, self.y - 16, self.data.anim_open, 4, False)
    
'''

'''
class Switch(Entity):
    def __init__(self, tile_x, tile_y, entity_data):
        Entity.__init__(self, tile_x, tile_y, entity_data)
        self.on = False
        
    def activate(self):
        if not self.on:
            self.on = True
            game.barrier.activate_switch() # FIXME
            sound.play_sfx(sfx.attack_miss, len(sfx.attack_miss), True)
        else:
            game.show_text([['It seems that', 'it\'s activated.']])
        
    def draw(self):
        if self.on:
            screen.blit(gfx.switch_on, (self.x - 7) - camera.x, (self.y - 12) - camera.y)
        else:
            screen.blit(gfx.switch_off, (self.x - 7) - camera.x, (self.y - 12) - camera.y)
'''
    
'''
class Barrier(Entity):
    def __init__(self, tile_x, tile_y, entity_data):
        Entity.__init__(self, tile_x, tile_y, entity_data)
        self.switch_count = 2 # FIXME
        
    def hit(self, player):
        return True
        
    def activate_switch(self):
        # FIXME
        self.switch_count -= 1
        if self.switch_count == 0: game.doors.remove(self)

    def draw(self):
        screen.blit(gfx.barrier_closed, (self.x - 8) - camera.x, (self.y - 16) - camera.y)
'''
'''
class Spike(Entity):
    def __init__(self, tile_x, tile_y, entity_data):
        Entity.__init__(self, tile_x, tile_y, entity_data)
        self.up = (tile_x % 2 == 0 and tile_y % 2 == 0) or (tile_x % 2 == 1 and tile_y % 2 == 1)
        if self.up: self.counter = 40
        else: self.counter = 55 # Shift start to sync the spikes: (70-40) / 2 = 15
        
    def update(self):
        if self.up and self.counter > 6 and self.collide_with(self.x, self.y, game.player):
            game.player.damage(1)
        
        self.counter -= 1
        if self.counter == 0:
            self.up = not self.up
            if self.up: self.counter = 40
            else: self.counter = 70
        
    def draw(self):
        if self.counter < 6:
            screen.blit(gfx.spike_middle, (self.x - 7) - camera.x, (self.y - 16) - camera.y)
        elif self.up:
            screen.blit(gfx.spike_up, (self.x - 7) - camera.x, (self.y - 16) - camera.y)
        else:
            screen.blit(gfx.spike_down, (self.x - 7) - camera.x, (self.y - 16) - camera.y)
'''

'''
class Signpost(Entity):
    def __init__(self, tile_x, tile_y, entity_data, text):
        Entity.__init__(self, tile_x, tile_y, entity_data)
        self.text = text
        
    def activate(self):
        game.show_text(self.text)
        sound.play_sfx(sfx.select, len(sfx.select), True)
                
    def draw(self):
        screen.blit(gfx.signpost_idle, (self.x - 5) - camera.x, (self.y - 12) - camera.y)
'''
    
class Game:
    def __init__(self):
        self.map_data = bytearray((MAP_WIDTH * MAP_HEIGHT) // 2)
        
        self.tilemap = pygame.tilemap.Tilemap(MAP_WIDTH, MAP_HEIGHT, self.map_data)
        
        self.tilemap.set_tile(0x3, TILE_WIDTH, TILE_HEIGHT, gfx.tile_cliff)
        self.tilemap.set_tile(0x4, TILE_WIDTH, TILE_HEIGHT, gfx.tile_stalk_1)
        self.tilemap.set_tile(0x5, TILE_WIDTH, TILE_HEIGHT, gfx.tile_tree)
        self.tilemap.set_tile(0x8, TILE_WIDTH, TILE_HEIGHT, gfx.tile_water_1)
        self.tilemap.set_tile(dt.TILE_GROUND, TILE_WIDTH, TILE_HEIGHT, gfx.tile_path)
        self.tilemap.set_tile(dt.TILE_GRASS, TILE_WIDTH, TILE_HEIGHT, gfx.tile_grass)
        
    def new_game(self, world):
        self.world = world
        world.reset()
        self.hp = data.player.hp
        self.key = 0
        self.has_sword = False #DEBUG_SWORD
        self.text = None
        self.load_map(world.starting_map)
        self.game_over_counter = 50
        self.paused = False
        self.lanea = True
        
        #if not self.player: print("ERROR no player found!")
        camera.look_at(self.player.x - 55, self.player.y - 48)
        
        #if not SKIP_INTRO and world.intro_text:
        if world.intro_text:
            self.player.state = STATE_SLEEP
            self.show_text(world.intro_text)
            sound.play_sfx(sfx.select, len(sfx.select), True)
        
    def load_map(self, map_data):
        self.current_map = map_data
        self.player = None
        self.enemies = []
        self.collectibles = []
        self.doors = []
        self.bushes = []
        self.spikes = []
        self.signposts = []
        
        if map_data.custom_ground: self.tilemap.set_tile(0x6, TILE_WIDTH, TILE_HEIGHT, map_data.custom_ground)
        if map_data.custom_solid: self.tilemap.set_tile(0xA, TILE_WIDTH, TILE_HEIGHT, map_data.custom_solid)
        
        if map_data.tile_wall:
            self.tilemap.set_tile(0xC, TILE_WIDTH, TILE_HEIGHT, map_data.tile_wall[0])
            self.tilemap.set_tile(0xD, TILE_WIDTH, TILE_HEIGHT, map_data.tile_wall[1])
            self.tilemap.set_tile(0xE, TILE_WIDTH, TILE_HEIGHT, map_data.tile_wall[2])
            self.tilemap.set_tile(0xF, TILE_WIDTH, TILE_HEIGHT, map_data.tile_wall[3])
            
        self.tile_anim_counter = 1
        self.tile_anim_index = 0
        
        gc.collect()
        #print ("free RAM before map load:", gc.mem_free())
 
        for ix in range(0, MAP_WIDTH):
            for iy in range(0, MAP_HEIGHT):
                tid = get_tile_at(map_data.tiles, ix, iy)
                if tid == 0x0:
                    self.player = Player(ix, iy, data.player)
                    tid = dt.TILE_GRASS
                elif tid == dt.TILE_ENTITY_1:
                    self.create_entity(ix, iy, map_data.entity_1)
                    tid = map_data.entity_1_tid
                elif tid == dt.TILE_ENTITY_2:
                    self.create_entity(ix, iy, map_data.entity_2)
                    tid = map_data.entity_2_tid
                elif tid == dt.TILE_ENTITY_3:
                    self.create_entity(ix, iy, map_data.entity_3)
                    tid = map_data.entity_3_tid
                elif tid == dt.TILE_ENTITY_4:
                    self.create_entity(ix, iy, map_data.entity_4)
                    tid = map_data.entity_4_tid
                elif tid == dt.TILE_ENTITY_5:
                    self.create_entity(ix, iy, map_data.entity_5)
                    tid = map_data.entity_5_tid
                elif tid == dt.TILE_ENTITY_6:
                    self.create_entity(ix, iy, map_data.entity_6)
                    tid = map_data.entity_6_tid
                elif tid == 0x7:
                    # Wall resolution
                    top = False
                    if iy > 0 and get_tile_at(map_data.tiles, ix, iy - 1) == 0x7: top = True
                    bottom = False
                    if iy < MAP_HEIGHT - 1 and get_tile_at(map_data.tiles, ix, iy + 1) == 0x7: bottom = True
                    
                    if top and bottom:
                        tid = 0xF
                    elif top and not bottom:
                        tid = 0xE
                    elif not top and bottom:
                        tid = 0xD
                    else:
                        tid = 0xC

                set_tile_at(self.map_data, ix, iy, tid)
                    
                
        for sp in map_data.signposts:
            signpost = GenericEntity(sp['x'], sp['y'], data.signpost)
            signpost.text = sp['text']
            self.signposts.append(signpost)

       # print ("free RAM after map load:", gc.mem_free())
             
    def create_entity(self, x, y, id):
        if id == dt.ENTITY_BUSH:
            self.bushes.append(GenericEntity(x, y, data.bush))
        elif id == dt.ENTITY_DOOR:
            self.doors.append(GenericEntity(x, y, data.door))
        elif id == dt.ENTITY_SLIME:
            self.enemies.append(Enemy(x, y, data.enemy_slime))
        elif id == dt.ENTITY_SLIME_STRONG:
            self.enemies.append(Enemy(x, y, data.enemy_slime_strong))
        elif id == dt.ENTITY_SPIKE:
            self.spikes.append(GenericEntity(x, y, data.spike))
        elif id == dt.ENTITY_BARRIER:
            self.barrier = GenericEntity(x, y, data.barrier) # FIXME
            self.doors.append(self.barrier)
        elif id == dt.ENTITY_SWITCH:
            self.signposts.append(GenericEntity(x, y, data.switch))
        elif id >= dt.ENTITY_KEY:
            if not self.current_map.is_collected_at(x, y):
                self.collectibles.append(Collectible(x, y, data.collectible[id]))
            
            
    def load_next_map(self, dx, dy):
        next_map = self.world.get_map_at(self.current_map.x + dx, self.current_map.y + dy)
        if next_map:
            
            previous_x = self.player.x
            previous_y = self.player.y
            
            self.load_map(next_map)
            
            self.player = Player(0, 0, data.player)
            dir = get_dir(dx, dy)
            if dir == DIR_UP:
                self.player.x = previous_x
                self.player.y = MAP_HEIGHT_PX - 1
            elif dir == DIR_DOWN:
                self.player.x = previous_x
                self.player.y = 16
            elif dir == DIR_LEFT:
                self.player.x = MAP_WIDTH_PX - 8
                self.player.y = previous_y
            elif dir == DIR_RIGHT:
                self.player.x = 8
                self.player.y = previous_y
            
            self.player.dir = dir
            camera.look_at(self.player.x - 55, self.player.y - 48)
            
        else:
            show_scene(EndScene())
        
    def is_tile_solid(self, x, y):
        # This method inlines get_tile_at() in order to reduce stack usage.
        tid = self.map_data[y * MAP_WIDTH // 2 + x // 2]
        if x % 2 == 0:
            tid = (tid & 0xF0) >> 4
        else:
            tid = tid & 0x0F
        return tid == 0x3 or tid == 0x5 or tid == 0x8 or tid == 0xA or tid >= 0xC
        
    def map_collide(self, x, y, hitbox):
        # In order to avoid 2 for loop this collision routine only works with hitbox smaller than a tile.
        # This most likely is a premature optimization but well...
        x1 = (x + hitbox.x) // TILE_WIDTH
        y1 = (y + hitbox.y) // TILE_HEIGHT
        if self.is_tile_solid(x1, y1): return True
        
        x2 = (x + hitbox.x + hitbox.width) // TILE_WIDTH
        if self.is_tile_solid(x2, y1): return True
        
        y2 = (y + hitbox.y + hitbox.height) // TILE_HEIGHT
        if self.is_tile_solid(x1, y2): return True
        if self.is_tile_solid(x2, y2): return True
        
    def show_text(self, text):
        self.text = text
        self.text_index = 0
                    
    def update(self):
        if not self.text and not self.player.state == STATE_DEAD and input_c:
            #if SKIP_INTRO:
            #    game.new_game(data.world)
            #    show_scene(game)
            #else:
            self.paused = not self.paused
        if self.paused: return
    
        if self.text:
            if input_a:
                self.text_index += 1
                if self.text_index == len(self.text):
                    self.text = None
                    if self.player.state == STATE_SLEEP: self.player.state = STATE_IDLE
                sound.play_sfx(sfx.select, len(sfx.select), True)
        else:
            for e in self.enemies: e.update()
            for e in self.collectibles: e.update()
            
            # Updating spikes seems to be a bottleneck, so it's inlined here..
            # Also player rect is calculated only once
            rect_1.x = self.player.x + self.player.data.hitbox.x
            rect_1.y = self.player.y + self.player.data.hitbox.y
            rect_1.width = self.player.data.hitbox.width
            rect_1.height = self.player.data.hitbox.height
            for e in self.spikes:
                if e.up and e.counter > 6 and e.collide_with_rect(rect_1):
                    game.player.damage(1)
                
                e.counter -= 1
                if e.counter == 0:
                    e.up = not e.up
                    if e.up: e.counter = 40
                    else: e.counter = 70
            
            self.player.update()
            camera.look_at(self.player.x - 55, self.player.y - 48)
            
        if self.player.state == STATE_DEAD:
            self.game_over_counter -= 1
            if self.game_over_counter == 0:
                show_scene(GameOverScene())
        
    def draw(self):
        if self.paused:
            draw_text_centered(SCREEN_WIDTH // 2 + 1, 42, "PAUSED", 0x1)
            draw_text_centered(SCREEN_WIDTH // 2, 41, "PAUSED", 0xF)
            return
            
        self.tile_anim_counter -= 1
        if self.tile_anim_counter == 0:
            if self.tile_anim_index == 0:
                self.tilemap.set_tile(0x4, TILE_WIDTH, TILE_HEIGHT, gfx.tile_stalk_1)
                self.tilemap.set_tile(0x8, TILE_WIDTH, TILE_HEIGHT, gfx.tile_water_1)
                self.tile_anim_index = 1
            else:
                self.tilemap.set_tile(0x4, TILE_WIDTH, TILE_HEIGHT, gfx.tile_stalk_2)
                self.tilemap.set_tile(0x8, TILE_WIDTH, TILE_HEIGHT, gfx.tile_water_2)
                self.tile_anim_index = 0
            self.tile_anim_counter = 30
            
        self.tilemap.draw(-camera.x, -camera.y)
        for e in self.spikes: e.draw()
        for e in self.collectibles: e.draw()
        for e in self.enemies: e.draw()
        for e in self.bushes: e.draw()
        for e in self.doors: e.draw()
        for e in self.signposts: e.draw()
        self.player.draw()
        
        for i in range(0, self.hp):
            screen.blit(gfx.ui_hearth, SCREEN_WIDTH - 11 * (i + 1), 2)
            
        item_x = 1
        if self.has_sword:
            screen.blit(gfx.collectible_sword_idle, item_x, 1)
            item_x += 11
            
        for i in range(0, self.key):
            screen.blit(gfx.collectible_key_idle, item_x, 1)
            item_x += 11
            
        if self.text:
            screen.fill(0x0, TEXT_RECT)
            txt = self.text[self.text_index]
            if type(txt) is list:
                if len(txt) == 1:
                    #machine.draw_text(36, 64, txt[0], 0xF)
                    draw_text_centered(68, 64, txt[0], 0xF)
                else:
                    machine.draw_text(40, 59, txt[0], 0xF)
                    machine.draw_text(48, 69, txt[1], 0xF)
                screen.blit(gfx.portrait_lanea, -12, TEXT_RECT.y)
                if self.player.state == STATE_SLEEP: self.player.state = STATE_IDLE
            else:
                draw_text_centered(SCREEN_WIDTH // 2, 64, txt, 0xF)
                
            camera.look_at(self.player.x - 55, self.player.y - 45)

class TitleScene:
    def __init__(self):
        self.press_start_counter = 90
        self.press_start_visible = False
        
    def update(self):
        if input_c:
            game.new_game(data.world)
            show_scene(game)
            
    def draw(self):
        screen.fill(0x0, screen.get_rect())
        screen.blit(gfx.title, 17, 8)
        self.press_start_counter -= 1
        if self.press_start_counter == 0:
            self.press_start_visible = not self.press_start_visible
            self.press_start_counter = 12
        
        if self.press_start_visible: draw_text_centered(SCREEN_WIDTH // 2, 74, "Press Start", 0xF)
        
class EndScene:
    def update(self):
        if input_c:
            sound.play_sfx(sfx.select, len(sfx.select), True)
            show_scene(TitleScene())
            
    def draw(self):
        screen.fill(0x0, screen.get_rect())
        draw_text_centered(SCREEN_WIDTH // 2, 41, "To be continued...", 0xF)
        
class GameOverScene:
    def update(self):
        if input_c:
            sound.play_sfx(sfx.select, len(sfx.select), True)
            show_scene(TitleScene())
            
    def draw(self):
        screen.fill(0x0, screen.get_rect())
        draw_text_centered(SCREEN_WIDTH // 2, 41, "GAME OVER", 0xF)

input_x = 0
input_y = 0

scene = None
def show_scene(s):
    global scene
    scene = s

    gc.collect()
    #print ("free RAM:", gc.mem_free())
    
game = Game()

#if SKIP_INTRO:
#    game.new_game(data.world)
#    show_scene(game)
#else:
show_scene(TitleScene())

while True:
    # Main update loop.
    
    input_a = False
    input_b = False
    input_c = False
    eventtype = pygame.event.poll()
    if eventtype != pygame.NOEVENT:
        if eventtype.type == pygame.KEYDOWN:
            if eventtype.key == pygame.K_RIGHT: input_x = 1
            if eventtype.key == pygame.K_LEFT:  input_x = -1
            if eventtype.key == pygame.K_DOWN:  input_y = 1
            if eventtype.key == pygame.K_UP:    input_y = -1
            if eventtype.key == pygame.BUT_A:   input_a = True
            if eventtype.key == pygame.BUT_B:   input_b = True
            if eventtype.key == pygame.BUT_C:   input_c = True
                
        if eventtype.type == pygame.KEYUP:
            if eventtype.key == pygame.K_RIGHT: input_x = 0
            if eventtype.key == pygame.K_LEFT:  input_x = 0
            if eventtype.key == pygame.K_DOWN:  input_y = 0
            if eventtype.key == pygame.K_UP:    input_y = 0
            
    scene.update()
    camera.update()
    scene.draw()

    pygame.display.flip()