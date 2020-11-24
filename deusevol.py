import pygame
from itertools import product
import math
import numpy as np
import time

width = 740
height = 480
FPS = 60
cellscale = 3
ts_scale = [1/60, 1, 60, 60*2, 60*4, 60*6, 60*12, 60*24, 60*24*7, 60*24*30, 60*24*365]
ts_index = 1
time_speed = 1000*60*ts_scale[ts_index]

# 0 - one year in a second, 
# 1 - one year in a minute, 
# 2 - one year in an hour
# 3 - one year in 2 hours
# 3 - one year in 4 hours
# 3 - one year in 6 hours
# 3 - one year in 12 hours
# 3 - one year in a day
# 3 - one year in a week
# 3 - one year in a month
# 3 - one year in a year

cellsize = 16 + 16 * cellscale
camera = [0, 0]
hairm = ('graphics/hairshort.png', 'graphics/hairmiddle.png', \
         'graphics/hairmohawk.png')
hairf = ('graphics/hairlong.png', 'graphics/hairmiddlebig.png', \
         'graphics/hairmiddle.png')
haira = ('graphics/hairafro.png', 'graphics/hairshortest.png')
hairb = ['graphics/hairback.png']
hairunique = ('graphics/hairbald.png')
clothesm = [0, 'graphics/bikinim.png']
clothesf = [0, 'graphics/bikinif.png']

def tile_prepare(image, color=0, scale=(cellsize, cellsize), flip=False):
    tile = pygame.image.load(image)
    if flip:
        tile = pygame.transform.flip(tile, True, False)
    tile = pygame.transform.scale(tile, scale)
    if color:
        colortile = pygame.Surface(tile.get_size()).convert_alpha()
        colortile.fill(color)
        tile.blit(colortile, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
    else:
        tile.blit(tile, (0,0))
    return tile

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Deus Evolution')
clock = pygame.time.Clock()
dt = 0
end_coords = [0, 0]

def truncated_normal(mean, stddev, minval, maxval):
    return np.clip(np.random.normal(mean, stddev), minval, maxval)

class Human(pygame.sprite.Sprite):
    def __init__(self, pos, x, y, gmelanine, gskincrange, gskinbalance, \
                 female, gmuscularity, gspeed, ghairred, ghairlength, age=0):
        pygame.sprite.Sprite.__init__(self)
        self.birth = pygame.time.get_ticks()
        self.detage = age
        self.age = age
        self.ghairlength = ghairlength
        self.gskincrange = gskincrange
        self.gskinbalance = gskinbalance
        self.ghairred = ghairred
        self.pos = pygame.Vector2(pos)
        self.player = False
        self.married = False
        self.dead = False
        self.clotheschanged = True
        self.colorchanged = True
        self.female = female
        self.melanine = gmelanine
        self.gspeed = gspeed
        self.flipsprite = False
        self.muscularity = gmuscularity - (female * 0.3 * gmuscularity) 
        self.width = 0
        self.clothes = [0, 0, 0, 0, 0, 0, 0]
        # [underwear, shirt, coat, legs, arms, hat, mask]
        self.attract = self.melanine
        self.speed = gspeed - (female * 0.2 * gspeed) - (gmelanine * 0.1 * gspeed)
        if self.female:
            self.bodynude = pygame.image.load('graphics/bodyf.png')
        else:
            self.bodynude = pygame.image.load('graphics/bodym.png')
        self.body = self.bodynude.copy()
        if self.melanine < 0.3:
            self.hairstyle = haira[np.random.randint(0, len(haira))]
        else:
            if self.female:
                self.hairstyle = hairf[np.random.randint(0, len(hairf))]
            else:
                self.hairstyle = hairm[np.random.randint(0, len(hairm))]
        self.build_sprite()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speedx = 0
        self.speedy = 0

    def build_sprite(self):
        self.image = pygame.Surface((16, 17))
        self.image = pygame.image.load('graphics/head.png')
        self.image.blit(self.image, (0, 0))
        self.image = pygame.transform.scale(self.image, (cellsize, cellsize))
        self.hairlength = self.ghairlength * self.melanine
        self.greyhair()
        self.hairback = 0
        self.ghairlight = self.melanine * self.gskincrange
        hred, hgreen, hblue = 30, 30, 30
        hred += int(self.ghairlight * 225)
        hgreen += int(((hred - 30)/2) + ((hred - 30)/2) * (1 - self.ghairred))
        if hred > 210 and self.ghairred > 0.5:
            self.frek = tile_prepare('graphics/freckles.png', (hred, hgreen, hblue))
            self.frek.set_alpha(255 * (self.ghairred - 0.5) * 2)
            self.image.blit(self.frek, (0, 0))
        hredgrey = (255 - hred) * ((self.hairgreyness - 0.5) * 2)
        hred = int((abs(hredgrey) + hredgrey)/2 + hred)
        hgreen = int(hgreen + ((hred - hgreen) * self.hairgreyness))
        hblue = int(hblue + ((hred - hblue) * self.hairgreyness))
        red = 30 + int(225 * self.melanine)
        blue = int(red * 0.6 * self.gskincrange)
        green = int(blue + (0.4 * (red - blue)) + (0.4 * (red - blue)) * \
                    (1 - self.gskinbalance))
        self.colorimage = pygame.Surface(self.image.get_size()).convert_alpha()
        self.colorimage.fill((red, green, blue))
        self.image.blit(self.colorimage, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
        if self.colorchanged:
            self.colorbody = pygame.Surface(self.body.get_size()).convert_alpha()
            self.colorbody.fill((red, green, blue))
            self.body.blit(self.colorbody, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
            self.colorchanged = False
        if self.clotheschanged:
            self.body_wear()
            self.clotheschanged = False
        if not self.female:
            self.width = int((1 - self.muscularity) * 0.3 * cellsize)
            self.body = pygame.transform.scale(self.body, (cellsize - self.width, cellsize))
        else:
            self.body = pygame.transform.scale(self.body, (cellsize, cellsize))
            backlength = int(self.hairlength * (cellsize * (10/16)))
            self.hairback = tile_prepare(hairb[0], (hred, hgreen, hblue), scale=(int(cellsize * (9/16)), backlength))
        self.image.blit(self.body, (self.width/2, 0))
        self.hair = pygame.image.load(self.hairstyle)
        self.hair = pygame.transform.scale(self.hair, (cellsize, cellsize))
        self.bodylayer = self.image.copy()
        self.shadow = tile_prepare('graphics/shadow.png')
        self.image.blit(self.shadow, (0, 0))
        if self.hairback:
            self.image.blit(self.hairback, (cellsize * (4/16), cellsize * (4/16)))
        self.image.blit(self.bodylayer, (0, 0))
        self.colorhair = pygame.Surface(self.hair.get_size()).convert_alpha()
        self.colorhair.fill((hred, hgreen, hblue))
        self.hair.blit(self.colorhair, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
        self.image.blit(self.hair, (0, 0))
        self.imageunflip = self.image
        self.imageflip = pygame.transform.flip(self.image, True, False)
        if self.flipsprite == True:
            self.image = self.imageflip

    def update(self, events=0, dt=clock.tick(FPS), x=0, y=0):
        self.age = self.detage + (pygame.time.get_ticks() - self.birth)/time_speed
        if self.rect.right in range(int(camera[0]), int(camera[0]) + width + cellsize) and \
        self.rect.bottom in range(int(camera[1]), int(camera[1]) + height + cellsize):
            self.build_sprite()
        move = pygame.Vector2((0, 0))
        move += (x, y)
        if move.length() > 0: move.normalize_ip()
        if x < 0:
            self.image = self.imageflip
        else:
            self.image = self.imageunflip 
        if self.rect.left < 2 * cellsize/16:
            move[0] = (abs(move[0]) + move[0])/2
        if self.rect.top < 2 * cellsize/16:
            move[1] = (abs(move[1]) + move[1])/2
        if self.rect.right > end_coords[0] - 2 * cellsize/16:
            move[0] = (move[0] - abs(move[0]))/2
        if self.rect.bottom > end_coords[1] - 2 * cellsize/16:
            move[1] = (move[1] - abs(move[1]))/2
        self.pos += move*(dt/5)*(cellsize/16)*0.3
        self.rect.center = self.pos
            
    def move_towards_player(self, beasty):
        dx, dy = beasty.rect.x - self.rect.x, beasty.rect.y - self.rect.y
        dist = math.hypot(dx, dy)
        if dist:
            dx, dy = dx/dist, dy/dist
        else:
            pass
        self.update(x=dx, y=dy)

    def move_awayfrom(self, beasty):
        dx, dy = beasty.rect.x - self.rect.x, beasty.rect.y - self.rect.y
        dist = math.hypot(dx, dy)
        if dist:
            dx, dy = dx/dist, dy/dist
        else:
#           self.rect.x += dx * (1 + self.speed) + 5
            pass
        self.update(x = -1 * dx, y = -1 * dy)
            
    def sex_behave(self):
        if not self.female and not self.married and not self.player:
            prefered = []
            for beast in beasts:
                if beast.female and not beast.married:
                    prefered.append(beast)
            while len(prefered) > 1:
                if abs(prefered[0].attract - self.attract) < abs(prefered[1].attract - self.attract):
                    prefered.remove(prefered[1])
                else:
                    prefered.remove(prefered[0])
            if prefered:
                if abs(self.pos[0] - prefered[0].pos[0]) > cellsize * (1/16) + 2 or \
                abs(self.pos[1] - prefered[0].pos[1]) > cellsize * (1/16) + 2:
                    self.move_towards_player(prefered[0])
                else:
                    if not prefered[0].player:
                        prefered[0].marry(self)
                        self.pos[0] = prefered[0].pos[0] + cellsize
                    
    def safety_behave(self):
        if self.female or self.married or self.dead:
            pass
        else:
            danger = []
            victim = []
            for beast in beasts:
                if beast.female or beast.married or beast.dead:
                    continue
                else:
                    if beast.muscularity > self.muscularity:
                        danger.append(beast)
                    else:
                        victim.append(beast)
            for beast in danger:
                if abs(self.rect.x - beast.rect.x) < 30 and \
                    abs(self.rect.y - beast.rect.y) < 30:
                        self.move_awayfrom(beast)
            for beast in victim:
                if abs(self.rect.x - beast.rect.x) < 20 and \
                    abs(self.rect.y - beast.rect.y) < 20:
                        self.move_towards_player(beast)
                if abs(self.rect.x - beast.rect.x) == 1 and \
                    abs(self.rect.y - beast.rect.y) == 1:
                        beast.die()

    def marry(self, beast):
        if self.age < 18:
            pass
        self.married = True
        beast.married = True
        self.clothes[0] = [1, (120, 190, 0)]
        self.clotheschanged = True
        beast.clothes[0] = [1, (120, 190, 0)]
        beast.clotheschanged = True
        chance = np.random.random()
        if self.female and not beast.female:
            self.givebirth(beast)
            if chance > 0.99:
                self.givebirth(beast, 2)
            if chance > 0.999:
                self.givebirth(beast, 3)
            if chance > 0.9999:
                self.givebirth(beast, 4)
            if chance > 0.99999:
                self.givebirth(beast, 5)
        if beast.female and not self.female:
            beast.givebirth(self)
            if chance > 0.99:
                beast.givebirth(self, 2)
            if chance > 0.999:
                beast.givebirth(self, 3)
            if chance > 0.9999:
                beast.givebirth(self, 4)
            if chance > 0.99999:
                beast.givebirth(self, 5)
            
    def givebirth(self, beast, lower=1):
        if self.age < 13:
            pass
        x = self.pos[0]
        y = self.pos[1] + cellsize * lower
        gmelanine = truncated_normal(\
            (self.melanine + beast.melanine)/2, 0.05, 0.001, 0.999)
        gskincrange = truncated_normal(\
            (self.gskincrange + beast.gskincrange)/2, 0.05, 0.001, 0.999)
        gskinbalance = truncated_normal(\
            (self.gskinbalance + beast.gskinbalance)/2, 0.05, 0.001, 0.999)
        female = np.random.choice((0, 1))
        gmuscularity = truncated_normal(\
            (self.muscularity + beast.muscularity)/2, 0.05, 0.001, 0.999)
        gspeed = truncated_normal(\
            (self.gspeed + beast.gspeed)/2, 0.05, 0.001, 0.999)
        ghairred = truncated_normal(\
            (self.ghairred + beast.ghairred)/2, 0.05, 0.001, 0.999)
        ghairlength = np.random.random()
        child = Human((x, y), x, y, gmelanine, gskincrange, \
                            gskinbalance, female, gmuscularity, gspeed, \
                            ghairred, ghairlength)
        beasts.append(child)
        
    def die(self):
        beasts.remove(self)
        self.speed = 0
        self.dead = True
        self.colorImage.fill((255, 255, 255))
        self.image.blit(self.colorImage, (0,0), special_flags = pygame.BLEND_RGBA_MULT)

    def body_wear(self):
        for cloth in self.clothes:
            if cloth:                
                if self.female:
                    self.cloth = pygame.image.load(clothesf[cloth[0]])
                    self.cloth = pygame.transform.scale(self.cloth, (cellsize, cellsize))
                else:
                    self.cloth = pygame.image.load(clothesm[cloth[0]])
                    self.width = int((1 - self.muscularity) * 0.3 * cellsize)
                    self.cloth = pygame.transform.scale(self.cloth, (cellsize - self.width, cellsize))
                self.colorcloth = pygame.Surface(self.hair.get_size()).convert_alpha()
                self.colorcloth.fill(cloth[1])
                self.cloth.blit(self.colorcloth, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
                self.body.blit(self.cloth, (0, 0))
        
    def greyhair(self):
        greyformula = 40 - (abs(self.age - 40) + (self.age - 40))/2
        greyformula = 1 - ((abs(greyformula) + greyformula)/2)/40
        self.hairgreyness = greyformula


class Player(Human):
    def __init__(self, pos, x, y, gmelanine, gskincrange, gskinbalance, \
                 female, gmuscularity, gspeed, ghairred, ghairlength, age):
        Human.__init__(self, pos, x, y, gmelanine, gskincrange, gskinbalance, \
                 female, gmuscularity, gspeed, ghairred, ghairlength, age)
        self.player = True

    def update(self, events, dt):
        self.age = self.detage + (pygame.time.get_ticks() - self.birth)/time_speed
        print(self.age)
        self.build_sprite()
        global camera
        pressed = pygame.key.get_pressed()
        move = pygame.Vector2((0, 0))
        if pressed[pygame.K_w]: 
            move += (0, -1)
        if pressed[pygame.K_a]: 
            self.flipsprite = True
            move += (-1, 0)
        if pressed[pygame.K_s]: 
            move += (0, 1)
        if pressed[pygame.K_d]: 
            self.flipsprite = False 
            move += (1, 0)
        if pressed[pygame.K_SPACE]:
            closest = []
            for i in beasts:
                if (abs(i.pos[0] - self.pos[0]) < (cellsize/16 * 5)) and \
                (abs(i.pos[1] - self.pos[1]) < (cellsize/16 * 5)) and not \
                i.player and not i.married:
                    closest.append(i)
            if len(closest) == 1:
                self.marry(closest[0])
        if move.length() > 0: move.normalize_ip()
        if self.rect.left < 2 * cellsize/16:
            move[0] = (abs(move[0]) + move[0])/2
        if self.rect.top < 2 * cellsize/16:
            move[1] = (abs(move[1]) + move[1])/2
        if self.rect.right > end_coords[0] - 2 * cellsize/16:
            move[0] = (move[0] - abs(move[0]))/2
        if self.rect.bottom > end_coords[1] - 2 * cellsize/16:
            move[1] = (move[1] - abs(move[1]))/2
        self.pos += move*(dt/5)*(cellsize/16)*0.3
        self.rect.center = self.pos
        if self.pos[0] > width/2 and self.pos[0] <= end_coords[0] - width/2:
            camera[0] = self.pos[0] - width/2
        elif self.pos[0] <= width/2:
            camera[0] = 0
        elif self.pos[0] > end_coords[0]:
            camera[0] = end_coords[0] - width/2
        if self.pos[1] > height/2 and self.pos[1] <= end_coords[1] - height/2:
            camera[1] = self.pos[1] - height/2
        elif self.pos[1] <= height/2:
            camera[1] = 0
        elif self.pos[0] > end_coords[1]:
            camera[0] = end_coords[1] - height/2


class YAwareGroup(pygame.sprite.Group):
    def by_y(self, spr):
        return spr.pos.y

    def draw(self, surface):
        sprites = self.sprites()
        surface_blit = surface.blit
        for spr in sorted(sprites, key=self.by_y):
            self.spritedict[spr] = surface_blit(spr.image, (spr.rect.x - camera[0], spr.rect.y - camera[1]))
        self.lostsprites = []


def setup_background():
    global end_coords
    screen.fill((0, 0, 0))
    plain = tile_prepare('graphics/grass.png', (110, 190, 60))
    plains = [0, plain]
    plant1 = tile_prepare('graphics/plants1.png', (150, 200, 80))
    plant1f = tile_prepare('graphics/plants1.png', (150, 200, 80), flip=True)
    plant2 = tile_prepare('graphics/plants2.png', (150, 200, 80))
    plant2f = tile_prepare('graphics/plants2.png', (150, 200, 80), flip=True)
    decs = [0, 0, 0, 0, 0, 0, plant1, plant1f, plant2, plant2f]
    tile_width, tile_height = plain.get_width(), plain.get_height()
    for x,y in product(range(0,tile_width * len(chunk[0][0]), tile_width),
                                 range(0,tile_height * len(chunk[0][0]),tile_height)):
        coord = [x - camera[0], y - camera[1]]
        screen.blit(plains[chunk[0][int(x/tile_width)][int(y/tile_height)]], coord)
        if decs[chunk[1][int(x/tile_width)][int(y/tile_height)]] != 0:
            screen.blit(decs[chunk[1][int(x/tile_width)][int(y/tile_height)]], coord)
        end_coords = [x + tile_width, y + tile_height]


chunk = np.array([np.ones((30, 30), dtype=int), \
                  np.random.randint(1, 10, size=(30, 30))])
    
setup_background()



all_sprites = pygame.sprite.Group()
x_coord = np.random.randint(0, int(end_coords[0]/cellsize)) * cellsize
y_coord = np.random.randint(0, int(end_coords[1]/cellsize)) * cellsize
player = Player((end_coords[0]/2, end_coords[1]/2), x_coord, y_coord, np.random.random(), \
                            np.random.random(), np.random.random(), \
                            np.random.choice((0, 1)), np.random.random(), \
                            np.random.random(), np.random.random(), \
                            np.random.random(), age=19)
beast_coords = []
beasts = []
sprites = []
beast_coords.append((x_coord, y_coord))
beasts.append(player)
while len(beast_coords) < 40:
    x_coord = np.random.randint(1, int(end_coords[0]/cellsize)) * cellsize
    y_coord = np.random.randint(1, int(end_coords[1]/cellsize)) * cellsize
    if (x_coord, y_coord) not in beast_coords:
        beast_coords.append((x_coord, y_coord))
        beasts.append(Human((x_coord, y_coord), x_coord, y_coord, np.random.random(), \
                            np.random.random(), np.random.random(), \
                            np.random.choice((0, 1)), np.random.random(), \
                            np.random.random(), np.random.random(), \
                            np.random.random(), age=19))
            
            
running = True
while running:
    sprites = YAwareGroup(beasts)
    events = pygame.event.get()
    for e in events:
        if e.type == pygame.QUIT:
            running = False
    sprites.update(events, dt)
    setup_background()
    sprites.draw(screen)
    dt = clock.tick(FPS)
    pygame.display.flip()
    for i in beasts:
#        i.safety_behave()
        i.sex_behave()
    
pygame.quit()
