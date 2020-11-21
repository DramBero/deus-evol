import pygame
from itertools import product
import math
import numpy as np

width = 740
height = 480
FPS = 60
cellsize = 16 * 3
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

def truncated_normal(mean, stddev, minval, maxval):
    return np.clip(np.random.normal(mean, stddev), minval, maxval)

class Human(pygame.sprite.Sprite):
    def __init__(self, x, y, gmelanine, gskincrange, gskinbalance, \
                 female, gmuscularity, gspeed, ghairred, ghairlength):
        pygame.sprite.Sprite.__init__(self)
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

    def update(self, x=0, y=0):
        self.speedx = x
        if self.speedx < 0:
            self.image = self.imageflip    
        else:
            self.image = self.imageunflip
        self.speedy = y
        self.rect.x += self.speedx
        self.rect.y += self.speedy
            
    def move_towards_player(self, beasty):
        dx, dy = beasty.rect.x - self.rect.x, beasty.rect.y - self.rect.y
        dist = math.hypot(dx, dy)
        if dist:
            dx, dy = dx/dist, dy/dist
        else:
            pass
        self.update(dx, dy)

    def move_awayfrom(self, beasty):
        dx, dy = beasty.rect.x - self.rect.x, beasty.rect.y - self.rect.y
        dist = math.hypot(dx, dy)
        if dist:
            dx, dy = dx/dist, dy/dist
        else:
            self.rect.x += dx * (1 + self.speed) + 5
            pass
        self.update(-1 * dx, -1 * dy)
            
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
                if abs(self.rect.x - prefered[0].rect.x) > 1 or \
                abs(self.rect.y - prefered[0].rect.y) > 1:
                    self.move_towards_player(prefered[0])
                else:
                    prefered[0].marry(self)
                    self.rect.x = prefered[0].rect.x + cellsize
                    
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
        if self.female:
            self.married = True
            beast.married = True
            self.body_wear(clothesf[0], (120, 190, 0))
            beast.body_wear(clothesm[0], (120, 190, 0))
            chance = np.random.random()
            self.givebirth(beast)
            if chance > 0.99:
                self.givebirth(beast, 2)
            if chance > 0.999:
                self.givebirth(beast, 3)
            if chance > 0.9999:
                self.givebirth(beast, 4)
            if chance > 0.99999:
                self.givebirth(beast, 5)
            
    def givebirth(self, beast, lower=1):
        x = self.rect.x
        y = self.rect.y + cellsize * lower
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
        child = Human(x, y, gmelanine, gskincrange, \
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
    def __init__(self, x, y, gmelanine, gskincrange, gskinbalance, \
                 female, gmuscularity, gspeed, ghairred, ghairlength):
        Human.__init__(self, x, y, gmelanine, gskincrange, gskinbalance, \
                 female, gmuscularity, gspeed, ghairred, ghairlength)
        self.player = True

    def update(self):
        self.speedx = 0
        self.speedy = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_a]:
            self.image = self.imageflip 
            self.speedx = -5
        if keystate[pygame.K_d]:
            self.image = self.imageunflip 
            self.speedx = 5
        if keystate[pygame.K_w]:
            self.speedy = -5
        if keystate[pygame.K_s]:
            self.speedy = 5
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.right > width:
            self.rect.right = width
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > height:
            self.rect.bottom = height


all_sprites = pygame.sprite.Group()

beast_coords = []
beasts = []
x_coord = np.random.randint(0, int(width/cellsize)) * cellsize
y_coord = np.random.randint(0, int(height/cellsize)) * cellsize
beast_coords.append((x_coord, y_coord))
beasts.append(Player(x_coord, y_coord, np.random.random(), \
                            np.random.random(), np.random.random(), \
                            np.random.choice((0, 1)), np.random.random(), \
                            np.random.random(), np.random.random(), \
                            np.random.random()))
while len(beast_coords) < 40:
    x_coord = np.random.randint(0, int(width/cellsize)) * cellsize
    y_coord = np.random.randint(0, int(height/cellsize)) * cellsize
    if (x_coord, y_coord) not in beast_coords:
        beast_coords.append((x_coord, y_coord))
        beasts.append(Human(x_coord, y_coord, np.random.random(), \
                            np.random.random(), np.random.random(), \
                            np.random.choice((0, 1)), np.random.random(), \
                            np.random.random(), np.random.random(), \
                            np.random.random()))


#beast1 = Human(beast_coords[0][0], beast_coords[0][1])

#all_sprites.add(player)
for i in beasts:
    all_sprites.add(i)


chunk = np.array([np.ones((40, 40), dtype=int), \
                  np.random.randint(1, 10, size=(40, 40))])


def setup_background():
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
        screen.blit(plains[chunk[0][int(x/tile_width)][int(y/tile_height)]], (x, y))
        if decs[chunk[1][int(x/tile_width)][int(y/tile_height)]] != 0:
            screen.blit(decs[chunk[1][int(x/tile_width)][int(y/tile_height)]], (x, y))
            
            
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    all_sprites.update()
    setup_background()
    all_sprites.draw(screen)
    pygame.display.flip()
    for i in beasts:
#        i.safety_behave()
        i.sex_behave()
pygame.quit()


