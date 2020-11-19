import pygame
from itertools import product
import math
import numpy as np

width = 740
height = 480
FPS = 60

# Задаем цвета
'''
from 0, 0, 0 to 256, 226, 216
g never more than r
b never more than g
b atleast 10 points less than g (except of g < 10)
g never more than 226
parameters:
    gskin_lightness, attract 1x
    gskin_col_range(r-g or g-b from 30 to 90), attract 1x
    gskin_balance(r-g/g-b), attract 0.5x
    
'''

def tile_prepare(image, color, flip=False):
    tile = pygame.image.load(image)
    if flip:
        tile = pygame.transform.flip(tile, True, False)
    tile = pygame.transform.scale(tile, (cellsize, cellsize))
    colortile = pygame.Surface(tile.get_size()).convert_alpha()
    colortile.fill(color)
    tile.blit(colortile, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
    return tile

# Создаем игру и окно
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Deus Evolution')
clock = pygame.time.Clock()
hairm = ('graphics/hairshort.png', 'graphics/hairmiddle.png', \
         'graphics/hairmohawk.png')
hairf = ('graphics/hairlong.png', 'graphics/hairmiddlebig.png', \
         'graphics/hairmiddle.png')
hairb = ['graphics/hairback.png']
hairunique = ('graphics/hairbald.png')
clothesm = ['graphics/bikinim.png']
clothesf = ['graphics/bikinif.png']
cellsize = 48

def truncated_normal(mean, stddev, minval, maxval):
    return np.clip(np.random.normal(mean, stddev), minval, maxval)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((16, 16))
        self.image.fill((50, 10, 0))
        self.rect = self.image.get_rect()
        self.rect.centerx = width / 2
        self.rect.bottom = height - 10
        self.speedx = 0
        self.speedy = 0

    def update(self):
        self.speedx = 0
        self.speedy = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_a]:
            self.speedx = -5
        if keystate[pygame.K_d]:
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


class Beast(pygame.sprite.Sprite):
    def __init__(self, x, y, gmelanine, gskincrange, gskinbalance, \
                 female, gmuscularity, gspeed, ghairred, ghairlength):
        pygame.sprite.Sprite.__init__(self)
        self.married = False
        self.dead = False
        self.female = female
        self.gmuscularity = gmuscularity
        self.gspeed = gspeed
        self.muscularity = gmuscularity - (female * 0.3 * gmuscularity) 
        self.image = pygame.Surface((16, 16))
        self.image = pygame.image.load('graphics/shadow.png')
        self.head = pygame.image.load('graphics/head.png')
        self.image.blit(self.head, (0, 0))
        self.image = pygame.transform.scale(self.image, (cellsize, cellsize))
        self.width = 0
        self.hairlength = ghairlength
        self.hairgreyness = 0
        self.hairback = 0
        if not self.female:
            self.body = pygame.image.load('graphics/bodym.png')
            if self.muscularity < 0.25:
                self.width = int(cellsize * 0.3)
            elif self.muscularity < 0.5:
                self.width = int(cellsize * 0.2)
            elif self.muscularity < 0.74:
                self.width = int(cellsize * 0.1)
            self.body = pygame.transform.scale(self.body, (cellsize - self.width, cellsize))
            self.hair = pygame.image.load(hairm[np.random.randint(0, len(hairm))])
            self.hair = pygame.transform.scale(self.hair, (cellsize, cellsize))
        else:
            self.body = pygame.image.load('graphics/bodyf.png')
            self.body = pygame.transform.scale(self.body, (cellsize, cellsize))
            backlength = int(self.hairlength * (cellsize * (10/16)))
            self.hairback = pygame.image.load(hairb[0])
            self.hairback = pygame.transform.scale(self.hairback, (int(cellsize * (9/16)), backlength))
            self.hair = pygame.image.load(hairf[np.random.randint(0, len(hairf))])
            self.hair = pygame.transform.scale(self.hair, (cellsize, cellsize))
        self.image.blit(self.body, (self.width/2, 0))
        self.colorImage = pygame.Surface(self.image.get_size()).convert_alpha()
        self.gmelanine = gmelanine
        self.gskincrange = gskincrange
        self.gskinbalance = gskinbalance
        self.ghairlight = self.gmelanine * self.gskincrange
        self.ghairred = ghairred
        red = 30 + int(225 * self.gmelanine)
        if red > 50:
            blue = int((red - 50) * self.gskincrange)
        else:
            blue = int(red * self.gskincrange)
        green = int(blue + (0.5 * (red - blue)) + (0.5 * (red - blue)) * \
                    (1 - self.gskinbalance))
        self.colorImage.fill((red, green, blue))
        self.image.blit(self.colorImage, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
        red, green, blue = 30, 30, 30
        red += int(self.ghairlight * 225)
        green += int(((red - 30)/2) + ((red - 30)/2) * (1 - self.ghairred))
        if red > 210 and self.ghairred > 0.5:
            self.frek = tile_prepare('graphics/freckles.png', (red, green, blue))
            self.frek.set_alpha(255 * (ghairred - 0.5) * 2)
            self.image.blit(self.frek, (0, 0))
        if self.hairgreyness < 0.5:
            green = green + ((red - green) * (self.hairgreyness * 2))
            blue = blue + ((red - blue) * (self.hairgreyness * 2))
        else:
            red = red + ((255 - red) * ((self.hairgreyness - 0.5) * 2))
            green = red
            blue = green
        if self.hairback:
            self.colorhairback = pygame.Surface(self.hairback.get_size()).convert_alpha()
            self.colorhairback.fill((red, green, blue))
            self.hairback.blit(self.colorhairback, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
            self.imagec = self.image.copy()
            self.image.blit(self.hairback, (cellsize * (4/16), cellsize * (4/16)))
            self.image.blit(self.imagec, (0, 0))
        self.colorhair = pygame.Surface(self.hair.get_size()).convert_alpha()
        self.colorhair.fill((red, green, blue))
        self.hair.blit(self.colorhair, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
        self.image.blit(self.hair, (0, 0))
        self.imageunflip = self.image
        self.imageflip = pygame.transform.flip(self.image, True, False)
        self.attract = self.gmelanine
        self.speed = gspeed - (female * 0.2 * gspeed) - \
        (gmelanine * 0.1 * gspeed)
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
        if not self.female and not self.married:
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
        child = Beast(x, y, gmelanine, gskincrange, \
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
        self.cloth = pygame.image.load(cloth)
        self.cloth = pygame.transform.scale(self.cloth, (cellsize - self.width, cellsize))
        self.colorcloth = pygame.Surface(self.hair.get_size()).convert_alpha()
        self.colorcloth.fill((color))
        self.cloth.blit(self.colorcloth, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
        self.image.blit(self.cloth, (self.width/2, 0))


all_sprites = pygame.sprite.Group()

beast_coords = []
beasts = []
while len(beast_coords) < 40:
    x_coord = np.random.randint(0, int(width/cellsize)) * cellsize
    y_coord = np.random.randint(0, int(height/cellsize)) * cellsize
    if (x_coord, y_coord) not in beast_coords:
        beast_coords.append((x_coord, y_coord))
        beasts.append(Beast(x_coord, y_coord, np.random.random(), \
                            np.random.random(), np.random.random(), \
                            np.random.choice((0, 1)), np.random.random(), \
                            np.random.random(), np.random.random(), \
                            np.random.random()))
        
player = Player()

#beast1 = Beast(beast_coords[0][0], beast_coords[0][1])

#all_sprites.add(player)
for i in beasts:
    all_sprites.add(i)


map1 = np.ones((40, 40), dtype=int)
map2 = np.random.randint(1, 10, size=(40, 40))
print(map2)


def setup_background():
    screen.fill((0, 0, 0))
    plain = tile_prepare('graphics/grass.png', (150, 180, 50))
    plains = [0, plain]
    plant1 = tile_prepare('graphics/plants1.png', (140, 200, 50))
    plant1f = tile_prepare('graphics/plants1.png', (140, 200, 50), flip=True)
    plant2 = tile_prepare('graphics/plants2.png', (140, 200, 50))
    plant2f = tile_prepare('graphics/plants2.png', (140, 200, 50), flip=True)
    decs = [0, 0, 0, 0, 0, 0, plant1, plant1f, plant2, plant2f]
    tile_width, tile_height = plain.get_width(), plain.get_height()
    for x,y in product(range(0,tile_width * len(map1[0]), tile_width),
                                 range(0,tile_height * len(map1[0]),tile_height)):
        screen.blit(plains[map1[int(x/tile_width)][int(y/tile_height)]], (x, y))
        if decs[map2[int(x/tile_width)][int(y/tile_height)]] != 0:
            screen.blit(decs[map2[int(x/tile_width)][int(y/tile_height)]], (x, y))
#        screen.blit(np.random.choice([plant1, plant1f, plant2, plant2f]), (x, y))

# Цикл игры
running = True
while running:
    # Держим цикл на правильной скорости
    clock.tick(FPS)
    # Ввод процесса (события)
    
    for event in pygame.event.get():
        # проверка для закрытия окна
        if event.type == pygame.QUIT:
            running = False

    # Обновление
    all_sprites.update()
    setup_background()
    # Рендеринг
    all_sprites.draw(screen)
    # После отрисовки всего, переворачиваем экран
    pygame.display.flip()
    for i in beasts:
        i.safety_behave()
        i.sex_behave()
        

pygame.quit()


