import pygame
from itertools import product
import math
import numpy as np

width = 740
height = 480
FPS = 60
cellscale = 3
cellsize = 16 + 16 * cellscale
camera = [0, 0]
hairm = ('graphics/hairshort.png', 'graphics/hairmiddle.png', \
         'graphics/hairmohawk.png')
hairf = ('graphics/hairlong.png', 'graphics/hairmiddlebig.png', \
         'graphics/hairmiddle.png')
haira = ('graphics/hairafro.png', 'graphics/hairshortest.png')
hairb = ['graphics/hairback.png']
hairunique = ('graphics/hairbald.png')
clothesm = ['graphics/bikinim.png']
clothesf = ['graphics/bikinif.png']

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
                 female, gmuscularity, gspeed, ghairred, ghairlength):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pygame.Vector2(pos)
        self.player = False
        self.married = False
        self.dead = False
        self.female = female
        self.gmuscularity = gmuscularity
        self.gspeed = gspeed
        self.muscularity = gmuscularity - (female * 0.3 * gmuscularity) 
        self.image = pygame.Surface((16, 17))
        self.image = pygame.image.load('graphics/head.png')
        self.image.blit(self.image, (0, 0))
        self.image = pygame.transform.scale(self.image, (cellsize, cellsize))
        self.width = 0
        self.hairlength = ghairlength * gmelanine
        self.hairgreyness = 0
        self.hairback = 0
        self.gmelanine = gmelanine
        self.gskincrange = gskincrange
        self.gskinbalance = gskinbalance
        self.ghairlight = self.gmelanine * self.gskincrange
        self.ghairred = ghairred
        hred, hgreen, hblue = 30, 30, 30
        hred += int(self.ghairlight * 225)
        hgreen += int(((hred - 30)/2) + ((hred - 30)/2) * (1 - self.ghairred))
        if hred > 210 and self.ghairred > 0.5:
            self.frek = tile_prepare('graphics/freckles.png', (hred, hgreen, hblue))
            self.frek.set_alpha(255 * (ghairred - 0.5) * 2)
            self.image.blit(self.frek, (0, 0))
        hredgrey = (255 - hred) * ((self.hairgreyness - 0.5) * 2)
        hred = int((abs(hredgrey) + hredgrey)/2 + hred)
        hgreen = int(hgreen + ((hred - hgreen) * self.hairgreyness))
        hblue = int(hblue + ((hred - hblue) * self.hairgreyness))
        if not self.female:
            self.body = pygame.image.load('graphics/bodym.png')
            self.width = int((1 - self.muscularity) * 0.3 * cellsize)
            self.body = pygame.transform.scale(self.body, (cellsize - self.width, cellsize))
            if self.gmelanine > 0.3:
                self.hair = pygame.image.load(hairm[np.random.randint(0, len(hairm))])
            else:
                self.hair = pygame.image.load(haira[np.random.randint(0, len(haira))])
        else:
            self.body = pygame.image.load('graphics/bodyf.png')
            self.body = pygame.transform.scale(self.body, (cellsize, cellsize))
            backlength = int(self.hairlength * (cellsize * (10/16)))
            self.hairback = tile_prepare(hairb[0], (hred, hgreen, hblue), scale=(int(cellsize * (9/16)), backlength))
            if self.gmelanine > 0.3:
                self.hair = pygame.image.load(hairf[np.random.randint(0, len(hairf))])
            else:
                self.hair = pygame.image.load(haira[np.random.randint(0, len(haira))])
        self.hair = pygame.transform.scale(self.hair, (cellsize, cellsize))
        self.image.blit(self.body, (self.width/2, 0))
        self.colorImage = pygame.Surface(self.image.get_size()).convert_alpha()
        red = 30 + int(225 * self.gmelanine)
        blue = int(red * 0.6 * self.gskincrange)
        green = int(blue + (0.4 * (red - blue)) + (0.4 * (red - blue)) * \
                    (1 - self.gskinbalance))
        self.colorImage.fill((red, green, blue))
        self.image.blit(self.colorImage, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
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
        self.attract = self.gmelanine
        self.speed = gspeed - (female * 0.2 * gspeed) - (gmelanine * 0.1 * gspeed)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speedx = 0
        self.speedy = 0

    def update(self, events=0, dt=clock.tick(FPS), x=0, y=0):
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
        self.married = True
        beast.married = True
        if self.female:
            self.body_wear(clothesf[0], (120, 190, 0))
        else:
            self.body_wear(clothesm[0], (120, 190, 0))
        if beast.female:
            beast.body_wear(clothesf[0], (120, 190, 0))
        else:
            beast.body_wear(clothesm[0], (120, 190, 0))
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
        x = self.pos[0]
        y = self.pos[1] + cellsize * lower
        gmelanine = truncated_normal(\
            (self.gmelanine + beast.gmelanine)/2, 0.05, 0.001, 0.999)
        gskincrange = truncated_normal(\
            (self.gskincrange + beast.gskincrange)/2, 0.05, 0.001, 0.999)
        gskinbalance = truncated_normal(\
            (self.gskinbalance + beast.gskinbalance)/2, 0.05, 0.001, 0.999)
        female = np.random.choice((0, 1))
        gmuscularity = truncated_normal(\
            (self.gmuscularity + beast.gmuscularity)/2, 0.05, 0.001, 0.999)
        gspeed = truncated_normal(\
            (self.gspeed + beast.gspeed)/2, 0.05, 0.001, 0.999)
        ghairred = truncated_normal(\
            (self.ghairred + beast.ghairred)/2, 0.05, 0.001, 0.999)
        ghairlength = np.random.random()
        child = Human((x, y), x, y, gmelanine, gskincrange, \
                            gskinbalance, female, gmuscularity, gspeed, \
                            ghairred, ghairlength)
        beasts.append(child)
        all_sprites.add(child)
        
    def die(self):
        beasts.remove(self)
        self.speed = 0
        self.dead = True
        self.colorImage.fill((255, 255, 255))
        self.image.blit(self.colorImage, (0,0), special_flags = pygame.BLEND_RGBA_MULT)

    def body_wear(self, cloth, color):
        self.image = self.imageunflip
        self.cloth = pygame.image.load(cloth)
        self.cloth = pygame.transform.scale(self.cloth, (cellsize - self.width, cellsize))
        self.colorcloth = pygame.Surface(self.hair.get_size()).convert_alpha()
        self.colorcloth.fill((color))
        self.cloth.blit(self.colorcloth, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
        self.image.blit(self.cloth, (self.width/2, 0))
        self.imageunflip = self.image
        self.imageflip = pygame.transform.flip(self.image, True, False)


class Player(Human):
    def __init__(self, pos, x, y, gmelanine, gskincrange, gskinbalance, \
                 female, gmuscularity, gspeed, ghairred, ghairlength):
        Human.__init__(self, pos, x, y, gmelanine, gskincrange, gskinbalance, \
                 female, gmuscularity, gspeed, ghairred, ghairlength)
        self.player = True

    def update(self, events, dt):
        global camera
        pressed = pygame.key.get_pressed()
        move = pygame.Vector2((0, 0))
        if pressed[pygame.K_w]: 
            move += (0, -1)
        if pressed[pygame.K_a]: 
            self.image = self.imageflip 
            move += (-1, 0)
        if pressed[pygame.K_s]: 
            move += (0, 1)
        if pressed[pygame.K_d]: 
            self.image = self.imageunflip 
            move += (1, 0)
        if pressed[pygame.K_SPACE]:
            closest = []
            for i in beasts:
                if (abs(i.pos[0] - self.pos[0]) < (cellsize/16 * 5)) and \
                (abs(i.pos[1] - self.pos[1]) < (cellsize/16 * 5)) and not \
                i.player and not i.married:
                    closest.append(i)
            if len(closest) == 1:
                print(closest)
                print(self.pos[0], self.pos[1])
                print(closest[0].pos[0], closest[0].pos[1])
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


all_sprites = pygame.sprite.Group()
x_coord = np.random.randint(0, int(width/cellsize)) * cellsize
y_coord = np.random.randint(0, int(height/cellsize)) * cellsize
player = Player((width/2, height/2), x_coord, y_coord, np.random.random(), \
                            np.random.random(), np.random.random(), \
                            np.random.choice((0, 1)), np.random.random(), \
                            np.random.random(), np.random.random(), \
                            np.random.random())
beast_coords = []
beasts = []
sprites = []
beast_coords.append((x_coord, y_coord))
beasts.append(player)
while len(beast_coords) < 30:
    x_coord = np.random.randint(1, int(width/cellsize)) * cellsize
    y_coord = np.random.randint(1, int(height/cellsize)) * cellsize
    if (x_coord, y_coord) not in beast_coords:
        beast_coords.append((x_coord, y_coord))
        beasts.append(Human((x_coord, y_coord), x_coord, y_coord, np.random.random(), \
                            np.random.random(), np.random.random(), \
                            np.random.choice((0, 1)), np.random.random(), \
                            np.random.random(), np.random.random(), \
                            np.random.random()))


chunk = np.array([np.ones((50, 50), dtype=int), \
                  np.random.randint(1, 10, size=(50, 50))])


def setup_background():
    global end_coords
    screen.fill((0, 0, 0))
    plain = tile_prepare('graphics/grass.png', (150, 180, 50))
    plains = [0, plain]
    plant1 = tile_prepare('graphics/plants1.png', (150, 200, 50))
    plant1f = tile_prepare('graphics/plants1.png', (150, 200, 50), flip=True)
    plant2 = tile_prepare('graphics/plants2.png', (150, 200, 50))
    plant2f = tile_prepare('graphics/plants2.png', (150, 200, 50), flip=True)
    decs = [0, 0, 0, 0, 0, 0, plant1, plant1f, plant2, plant2f]
    tile_width, tile_height = plain.get_width(), plain.get_height()
    for x,y in product(range(0,tile_width * len(chunk[0][0]), tile_width),
                                 range(0,tile_height * len(chunk[0][0]),tile_height)):
        coord = [x - camera[0], y - camera[1]]
        screen.blit(plains[chunk[0][int(x/tile_width)][int(y/tile_height)]], coord)
        if decs[chunk[1][int(x/tile_width)][int(y/tile_height)]] != 0:
            screen.blit(decs[chunk[1][int(x/tile_width)][int(y/tile_height)]], coord)
        end_coords = [x + tile_width, y + tile_height]
            
            
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


'''
        self.speedx = x
        if self.speedx < 0:
            self.image = self.imageflip    
        else:
            self.image = self.imageunflip
        self.speedy = y
        self.rect.x += self.speedx
        self.rect.y += self.speedy'''