import pygame
from itertools import product
import math
import numpy as np

width = 740
height = 480
FPS = 60
cellscale = 2
ts_scale = [1/60, 1, 60, 60*2, 60*4, 60*6, 60*12, 60*24, 60*24*7, 60*24*30, \
            60*24*365, 0]
ts_index = 4

# 0  - one year in a second, (1:31536000)
# 1  - one year in a minute, (1:525600)
# 2  - one year in an hour   (1:8760)
# 3  - one year in 2 hours   (1:4380)
# 4  - one year in 4 hours   (1:2190)
# 5  - one year in 6 hours   (1:1460)
# 6  - one year in 12 hours  (1:730)
# 7  - one year in a day     (1:365)
# 8  - one year in a week    (1:52)
# 9  - one year in a month   (1:12)
# 10 - one year in a year    (1:1)
# 11 - frozen                (1:0)

preshader = [1, 1, 1]
shader = [1, 1, 1]
tilesize = 32
step = 0
cur_year = 0
cur_day = 0
cur_date = 0
cur_hour = 0
cur_minute = 0
cur_tot_min = 0
cur_month = ''
time_speed = 1000*60*ts_scale[ts_index]
cellsize = tilesize + tilesize * cellscale
cam = [0, 0]
hairm = ('graphics32/hairm.png')
hairf = ('graphics32/hairf.png')
#haira = ('graphics/hairafro.png', 'graphics/hairshortest.png')
#hairb = ['graphics/hairback.png']
hairunique = ('graphics/hairbald.png')
clothesm = [0, 'graphics32/bikinim.png']
clothesf = [0, 'graphics32/bikinif.png']

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', \
          'August', 'September', 'October', 'November', 'December']


def tile_prepare(image, color=0, scale=(cellsize, cellsize), flip=False, \
                 shadert=0):
    tile = pygame.image.load(image)
    if flip:
        tile = pygame.transform.flip(tile, True, False)
    tile = pygame.transform.scale(tile, scale)
    if color:
        colort = [color[0], color[1], color[2]]
        if not shadert:
            shadert = shader
        colort[0] = colort[0] * shadert[0]
        colort[1] = colort[1] * shadert[1]
        colort[2] = colort[2] * shadert[2]
        colortile = pygame.Surface(tile.get_size()).convert_alpha()
        colortile.fill(colort)
        tile.blit(colortile, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
    else:
        tile.blit(tile, (0,0))
    return tile

pygame.init()
pygame.mixer.init()
pygame.font.init()
myfont = pygame.font.SysFont('Arial', 18, bold=True)
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Deus Evolution')
clock = pygame.time.Clock()
dt = 0
end_coords = [0, 0]

def truncated_normal(mean, stddev, minval, maxval):
    return np.clip(np.random.normal(mean, stddev), minval, maxval)


def create_anim(bodyparts, animframes, rotation=0):
    frames = []
    for i in range(len(animframes)):
        image = bodyparts[0].copy()
        for j in range(len(bodyparts)):
            part = bodyparts[j].copy()
            if rotation:
                part = pygame.transform.rotate(part, rotation[i][j])
            image.blit(part, animframes[i][j])
        frames.append(image)
    return frames


class Human(pygame.sprite.Sprite):
    def __init__(self, pos, x, y, gmelanine, gskincrange, gskinbalance, \
                 female, gmuscularity, gspeed, ghairred, ghairlength, age=0):
        pygame.sprite.Sprite.__init__(self)
        self.frame = 0
        self.step = 0
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
#        if self.melanine < 0.3:
#            self.hairstyle = haira[np.random.randint(0, len(haira))]
#        else:
        if self.female:
            self.hairstyle = hairf
#            self.hairstyle = hairf[np.random.randint(0, len(hairf))]
        else:
            self.hairstyle = hairm
#            self.hairstyle = hairm[np.random.randint(0, len(hairm))]
        self.body_build()
#        self.build_sprite()
        self.sprite_gen()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speedx = 0
        self.speedy = 0
        
    def body_build(self):
        red = int((30 + int(225 * self.melanine)))
        blue = int(red * 0.6 * self.gskincrange)
        green = int((blue + (0.4 * (red - blue)) + (0.4 * (red - blue)) * \
                    (1 - self.gskinbalance)))
        if self.female:
            armback = pygame.image.load('graphics32/farmback.png')
            legback = pygame.image.load('graphics32/flegback.png')
            body = pygame.image.load('graphics32/fbody.png')
            legfront = pygame.image.load('graphics32/flegfront.png') 
            armfront = pygame.image.load('graphics32/farmfront.png')
        else:
            armback = pygame.image.load('graphics32/marmback.png')
            legback = pygame.image.load('graphics32/mlegback.png')
            body = pygame.image.load('graphics32/mbody.png')
            legfront = pygame.image.load('graphics32/mlegfront.png') 
            armfront = pygame.image.load('graphics32/marmfront.png')
        armback = pygame.transform.scale(armback, (cellsize, cellsize))
        legback = pygame.transform.scale(legback, (cellsize, cellsize))
        body = pygame.transform.scale(body, (cellsize, cellsize))
        legfront = pygame.transform.scale(legfront, (cellsize, cellsize))
        armfront = pygame.transform.scale(armfront, (cellsize, cellsize))
        head = self.image = pygame.image.load('graphics32/head.png')
        head = pygame.transform.scale(head, (cellsize, cellsize))
        belly = pygame.image.load('graphics32/belly.png')
        belly = pygame.transform.scale(belly, (cellsize, cellsize))
        colorbody = pygame.Surface(armback.get_size()).convert_alpha()
        colorbody.fill((red, green, blue))
        for part in [armback, legback, body, legfront, armfront, head, belly]:
            part.blit(colorbody, (0,0), special_flags = pygame.BLEND_RGBA_MULT)        
        body.blit(belly, (0, 0))
        self.greyhair()
        self.hairback = 0
        self.ghairlight = self.melanine * self.gskincrange
        hred, hgreen, hblue = 30, 30, 30
        hred += int(self.ghairlight * 225)
        hgreen += int(((hred - 30)/2) + ((hred - 30)/2) * (1 - self.ghairred))
        hair = pygame.image.load(self.hairstyle)
        hair = pygame.transform.scale(hair, (cellsize, cellsize))
        colorhair = pygame.Surface(hair.get_size()).convert_alpha()
        colorhair.fill((hred, hgreen, hblue))
        hair.blit(colorhair, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
        head.blit(hair, (0, 0))
        bodyparts = [armback, legback, body, legfront, armfront, head]
        frame1 = [(0, -1), (0, 0), (0, -1), (0, 0), (0, -1), (0, -1)]
        frame2 = [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
        frame3 = [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
        frame4 = [(0, 0), (0, 0), (0, -1), (0, 0), (0, 0), (0, -1)]
        frame5 = [(0, -1), (0, 0), (0, -1), (0, 0), (0, -1), (0, -1)]
        frame6 = [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
        frame7 = [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
        frame8 = [(0, 0), (0, 0), (0, -1), (0, 0), (0, 0), (0, -1)]
        frame9 = [(0, -1), (0, 0), (0, -1), (0, 0), (0, -1), (0, -1)]
        frame10 = [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
        frame11 = [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
        frame12 = [(0, 0), (0, 0), (0, -1), (0, 0), (0, 0), (0, -1)]
        frame13 = [(0, -1), (0, 0), (0, -1), (0, 0), (0, -1), (0, -1)]
        frame14 = [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
        frame15 = [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
        frame16 = [(0, 0), (0, 0), (0, -1), (0, 0), (0, 0), (0, -1)]
        frames = [frame1, frame2, frame3, frame4, frame5, frame6, frame7, frame8, \
                  frame9, frame10, frame11, frame12, frame13, frame14, frame15, frame16]
        self.idle_anim = create_anim(bodyparts, frames)
        frame1 = [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
        frame2 = [(0, 0), (-3, -10), (0, 0), (-6, -6), (0, 0), (0, 0)]
        frame3 = [(0, 0), (-5, -14), (0, 0), (-14, -10), (0, 0), (0, 0)]
        frame4 = [(0, 0), (-7, -17), (0, 0), (-19, -14), (0, 0), (0, 0)]
        frame5 = [(0, 0), (-10, -19), (0, 0), (-25, -17), (0, 0), (0, 0)]
        frame6 = [(0, 0), (-7, -17), (0, 0), (-19, -14), (0, 0), (0, 0)]
        frame7 = [(0, 0), (-5, -14), (0, 0), (-14, -10), (0, 0), (0, 0)]
        frame8 = [(0, 0), (-3, -10), (0, 0), (-6, -6), (0, 0), (0, 0)]
        frame9 = [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
        frame10 = [(0, 0), (-8, -10), (0, 0), (-4, -6), (0, 0), (0, 0)]
        frame11 = [(0, 0), (-15, -14), (0, 0), (-8, -10), (0, 0), (0, 0)]
        frame12 = [(0, 0), (-19, -17), (0, 0), (-8, -14), (0, 0), (0, 0)]
        frame13 = [(0, 0), (-24, -19), (0, 0), (-8, -17), (0, 0), (0, 0)]
        frame14 = [(0, 0), (-19, -17), (0, 0), (-8, -14), (0, 0), (0, 0)]
        frame15 = [(0, 0), (-15, -14), (0, 0), (-8, -10), (0, 0), (0, 0)]
        frame16 = [(0, 0), (-8, -10), (0, 0), (-4, -6), (0, 0), (0, 0)]
        frames = [frame1, frame2, frame3, frame4, frame5, frame6, frame7, frame8, \
                  frame9, frame10, frame11, frame12, frame13, frame14, frame15, frame16]
        rot1 = [0, 0, 0, 0, 0, 0]
        rot2 = [0, -8, 0, 8, 0, 0]
        rot3 = [0, -15, 0, 15, 0, 0]
        rot4 = [0, -24, 0, 24, 0, 0]
        rot5 = [0, -33, 0, 33, 0, 0]
        rot6 = [0, -24, 0, 24, 0, 0]
        rot7 = [0, -15, 0, 15, 0, 0]
        rot8 = [0, -8, 0, 8, 0, 0]
        rot9 = [0, 0, 0, 0, 0, 0]
        rot10 = [0, 8, 0, -8, 0, 0]
        rot11 = [0, 15, 0, -15, 0, 0]
        rot12 = [0, 24, 0, -24, 0, 0]
        rot13 = [0, 33, 0, -33, 0, 0]
        rot14 = [0, 24, 0, -24, 0, 0]
        rot15 = [0, 15, 0, -15, 0, 0]
        rot16 = [0, 8, 0, -8, 0, 0]
        rots = [rot1, rot2, rot3, rot4, rot5, rot6, rot7, rot8, \
                rot9, rot10, rot11, rot12, rot13, rot14, rot15, rot16]
        self.run_anim = create_anim(bodyparts, frames, rots)
        self.anim = self.idle_anim

    def sprite_gen(self):
        self.body = self.anim[self.frame]
#        self.body = pygame.transform.scale(self.run_anim[self.frame], (cellsize, cellsize))
        self.image = pygame.Surface((tilesize, tilesize + (1/tilesize)))
        self.image = pygame.image.load('graphics32/heart.png')
        self.image.blit(self.image, (0, 0))
        self.image = pygame.transform.scale(self.image, (cellsize, cellsize))
    #    if hred > 210 and hairred > 0.5:
    #        frek = tile_prepare('graphics/freckles.png', \
    #                                 (int(hred), int(hgreen), \
    #                                  int(hblue)))
    #        frek.set_alpha(255 * (hairred - 0.5) * 2)
    #        image.blit(frek, (0, 0))
#        hredgrey = (255 - hred) * ((self.hairgreyness - 0.5) * 2)
#        hred = int(((abs(hredgrey) + hredgrey)/2 + hred))
#        hgreen = int((hgreen + ((hred - hgreen) * self.hairgreyness)))
#        hblue = int((hblue + ((hred - hblue) * self.hairgreyness)))
#        red = int((30 + int(225 * self.melanine)))
#        blue = int(red * 0.6 * self.gskincrange)
#        green = int((blue + (0.4 * (red - blue)) + (0.4 * (red - blue)) * \
#                    (1 - self.gskinbalance)))
#        colorimage = pygame.Surface(self.image.get_size()).convert_alpha()
#        colorimage.fill((red, green, blue))
#        self.image.blit(colorimage, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
#        if self.colorchanged:
#            colorbody = pygame.Surface(self.body.get_size()).convert_alpha()
#            colorbody.fill((red, green, blue))
#            self.body.blit(colorbody, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
#            self.colorchanged = False
#        if self.clotheschanged:
#            self.body_wear()
#            self.clotheschanged = False
        self.image.blit(self.body, (0, 0))
        bodylayer = self.image.copy()
        shadow = tile_prepare('graphics32/shadow.png')
        self.image.blit(shadow, (0, 0))
#        if hairback:
#            image.blit(hairback, (cellsize * (4/16), cellsize * (4/16)))
        self.image.blit(bodylayer, (0, 0))
#        self.image.blit(hair, (0, 0))
        imageflip = pygame.transform.flip(self.image, True, False)
        if self.flipsprite == True:
            self.image = imageflip
        sred = int(255 * shader[0])
        sgreen = int(255 * shader[1])
        sblue = int(255 * shader[2])
        colorshade = pygame.Surface(self.image.get_size()).convert_alpha()
        colorshade.fill((sred, sgreen, sblue))
        self.image.blit(colorshade, (0,0), special_flags = pygame.BLEND_RGBA_MULT)

    def build_sprite(self):
        self.image = pygame.Surface((tilesize, tilesize + (1/tilesize)))
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
            self.frek = tile_prepare('graphics/freckles.png', \
                                     (int(hred), int(hgreen), \
                                      int(hblue)))
            self.frek.set_alpha(255 * (self.ghairred - 0.5) * 2)
            self.image.blit(self.frek, (0, 0))
        hredgrey = (255 - hred) * ((self.hairgreyness - 0.5) * 2)
        hred = int(((abs(hredgrey) + hredgrey)/2 + hred))
        hgreen = int((hgreen + ((hred - hgreen) * self.hairgreyness)))
        hblue = int((hblue + ((hred - hblue) * self.hairgreyness)))
        red = int((30 + int(225 * self.melanine)))
        blue = int(red * 0.6 * self.gskincrange)
        green = int((blue + (0.4 * (red - blue)) + (0.4 * (red - blue)) * \
                    (1 - self.gskinbalance)))
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
#            backlength = int(self.hairlength * (cellsize * (10/16)))
#            self.hairback = tile_prepare(hairb[0], (hred, hgreen, hblue), scale=(int(cellsize * (9/16)), backlength))
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
        self.imageflip = pygame.transform.flip(self.image, True, False)
        if self.flipsprite == True:
            self.image = self.imageflip
        sred = int(255 * shader[0])
        sgreen = int(255 * shader[1])
        sblue = int(255 * shader[2])
        self.colorshade = pygame.Surface(self.hair.get_size()).convert_alpha()
        self.colorshade.fill((sred, sgreen, sblue))
        self.image.blit(self.colorshade, (0,0), special_flags = pygame.BLEND_RGBA_MULT)

    def update(self, events=0, dt=clock.tick(FPS), x=0, y=0):
        global step
        if time_speed:
            self.age = self.detage + \
            (pygame.time.get_ticks() - self.birth)/time_speed
        if self.rect.right in range(int(cam[0]), int(cam[0]) + width + cellsize) and \
        self.rect.bottom in range(int(cam[1]), int(cam[1]) + height + cellsize):
            self.sprite_gen()
        move = pygame.Vector2((0, 0))
        move += (x, y)
        if move.length() > 0: move.normalize_ip()
        time = pygame.time.get_ticks()
        if x < 0:
            self.flipsprite = True
        else:
            self.flipsprite = False
        if self.rect.left < 2 * cellsize/16:
            move[0] = (abs(move[0]) + move[0])/2
        if self.rect.top < 2 * cellsize/16:
            move[1] = (abs(move[1]) + move[1])/2
        if self.rect.right > end_coords[0] - 2 * cellsize/16:
            move[0] = (move[0] - abs(move[0]))/2
        if self.rect.bottom > end_coords[1] - 2 * cellsize/16:
            move[1] = (move[1] - abs(move[1]))/2
        if move:
            self.anim = self.run_anim
        else:
            self.anim = self.idle_anim
        if (time - self.step) > 40:
            if self.frame < (len(self.anim) - 1):
                self.frame += 1
            else:
                self.frame = 0
            self.step = time
        self.pos += move*(dt/5)*(cellsize/16)*0.3
        self.rect.center = self.pos
            
    def move_to_away(self, beasty, away=False):
        dx, dy = beasty.rect.x - self.rect.x, beasty.rect.y - self.rect.y
        dist = math.hypot(dx, dy)
        if not dist:
            pass
        dx, dy = dx/dist, dy/dist
        if away:
            self.update(x = -1 * dx, y = -1 * dy)
        else:
            self.update(x = dx, y = dy)
            
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
                    self.move_to_away(prefered[0])
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
                        self.move_to_away(beast)
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
                else:
                    self.cloth = pygame.image.load(clothesm[cloth[0]])
                self.cloth = pygame.transform.scale(self.cloth, (cellsize, cellsize))
                self.colorcloth = pygame.Surface(self.cloth.get_size()).convert_alpha()
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
        if time_speed:
            self.age = self.detage + (pygame.time.get_ticks() - self.birth)/time_speed
        self.sprite_gen()
        global step
        global cam
        pressed = pygame.key.get_pressed()
        move = pygame.Vector2((0, 0))
        time = pygame.time.get_ticks()
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
        if move:
            self.anim = self.run_anim
        else:
            self.anim = self.idle_anim
        if (time - self.step) > 40:
            if self.frame < (len(self.anim) - 1):
                self.frame += 1
            else:
                self.frame = 0
            self.step = time
        self.pos += move*(dt/5)*(cellsize/16)*0.16
        self.rect.center = self.pos
        if self.pos[0] > width/2 and self.pos[0] <= end_coords[0] - width/2:
            cam[0] = self.pos[0] - width/2
        elif self.pos[0] <= width/2:
            cam[0] = 0
        elif self.pos[0] > end_coords[0]:
            cam[0] = end_coords[0] - width/2
        if self.pos[1] > height/2 and self.pos[1] <= end_coords[1] - height/2:
            cam[1] = self.pos[1] - height/2
        elif self.pos[1] <= height/2:
            cam[1] = 0
        elif self.pos[0] > end_coords[1]:
            cam[0] = end_coords[1] - height/2


class YAwareGroup(pygame.sprite.Group):
    def by_y(self, spr):
        return spr.pos.y

    def draw(self, surface):
        sprites = self.sprites()
        surface_blit = surface.blit
        for spr in sorted(sprites, key=self.by_y):
            self.spritedict[spr] = surface_blit(spr.image, \
                           (spr.rect.x - cam[0], spr.rect.y - cam[1]))
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
        coord = [x - cam[0], y - cam[1]]
        screen.blit(plains[chunk[0][int(x/tile_width)][int(y/tile_height)]], coord)
        if decs[chunk[1][int(x/tile_width)][int(y/tile_height)]] != 0:
            screen.blit(decs[chunk[1][int(x/tile_width)][int(y/tile_height)]], coord)
        end_coords = [x + tile_width, y + tile_height]


def text_label():
    text1 = 'Year: ' + str(int(cur_year))
    text2 = 'Day: ' + str(int(cur_date)) + ' ' + cur_month
    text3 = 'Time: ' + str(int(cur_hour)) + ':' + str(int(cur_minute))
    texts = [text1, text2, text3]
    for i in range(len(texts)):
        textsurface = myfont.render(texts[i], True, (250, 250, 250))
        screen.blit(textsurface,(10,10 + 20 * i))


def get_month(cur_day, leap_year):
    cur_day = int(cur_day)
    num_month = 0
    cur_date = 1
    if cur_day in range(1, 32):
        num_month = 0
        cur_date = cur_day
    if not leap_year:
        if cur_day in range(32, 60):
            num_month = 1
            cur_date = cur_day - 31
        elif cur_day in range(60, 91):
            num_month = 2
            cur_date = cur_day - 59
        elif cur_day in range(91, 121):
            num_month = 3
            cur_date = cur_day - 90
        elif cur_day in range(121, 152):
            num_month = 4
            cur_date = cur_day - 120
        elif cur_day in range(152, 182):
            num_month = 5
            cur_date = cur_day - 151
        elif cur_day in range(182, 213):
            num_month = 6
            cur_date = cur_day - 181
        elif cur_day in range(213, 244):
            num_month = 7
            cur_date = cur_day - 212
        elif cur_day in range(244, 275):
            num_month = 8
            cur_date = cur_day - 243
        elif cur_day in range(275, 306):
            num_month = 9
            cur_date = cur_day - 274
        elif cur_day in range(306, 336):
            num_month = 10
            cur_date = cur_day - 305
        elif cur_day in range(335, 366):
            num_month = 11
            cur_date = cur_day - 334
    if leap_year:
        if cur_day in range(32, 61):
            num_month = 1
            cur_date = cur_day - 31
        elif cur_day in range(61, 92):
            num_month = 2
            cur_date = cur_day - 60
        elif cur_day in range(92, 122):
            num_month = 3
            cur_date = cur_day - 91
        elif cur_day in range(122, 153):
            num_month = 4
            cur_date = cur_day - 121
        elif cur_day in range(153, 183):
            num_month = 5
            cur_date = cur_day - 152
        elif cur_day in range(183, 214):
            num_month = 6
            cur_date = cur_day - 182
        elif cur_day in range(214, 245):
            num_month = 7
            cur_date = cur_day - 213
        elif cur_day in range(245, 276):
            num_month = 8
            cur_date = cur_day - 244
        elif cur_day in range(276, 307):
            num_month = 9
            cur_date = cur_day - 275
        elif cur_day in range(307, 336):
            num_month = 10
            cur_date = cur_day - 306
        elif cur_day in range(336, 367):
            num_month = 11
            cur_date = cur_day - 335
    return num_month, cur_date

def time_cycle():
    global cur_year
    global cur_day
    global cur_hour
    global cur_minute
    global cur_date
    global cur_month
    global cur_tot_min
    leap_year = False
    cur_year = pygame.time.get_ticks()/time_speed 
    if cur_year/4 - math.floor(cur_year/4) == 0:
        leap_year = True
    cur_day = 1 + (pygame.time.get_ticks()/time_speed - math.floor(cur_year)) * 365
    num_month, cur_date = get_month(cur_day, leap_year)
    cur_month = months[num_month]
    if leap_year:
        cur_day = cur_day + (cur_day * (1/365))
    cur_hour = (cur_day - math.floor(cur_day)) * 24
    cur_minute = (cur_hour - math.floor(cur_hour)) * 60
    cur_tot_min = (cur_day - math.floor(cur_day))


def day_night_cycle():
    global shader
#    dawn = 5:00 - 9:00
#    dusk = 20:00 - 22:00
#    sunset = 18:00 - 22:00
    if cur_tot_min > 8/24 and cur_tot_min < 20/24:
        darkness = 0
    elif cur_tot_min > 5/24 and cur_tot_min < 9/24:
        darkness = (1 - (cur_tot_min - 5/24) * 8) * 0.75
    elif cur_tot_min > 20/24 and cur_tot_min < 22/24:
        darkness = (cur_tot_min - 20/24) * 12 * 0.75
    else:
        darkness = 0.75
    if darkness < 0:
        darkness = 0
    elif darkness > 1:
        darkness = 1
    if cur_tot_min < 18/24 or cur_tot_min > 22/24:
        redness = 0
    else:
        redness = 1 - abs(1 - (cur_tot_min - 18/24) * 12)
    if redness < 0:
        redness = 0
    elif redness > 1:
        redness = 1
    if cur_tot_min < 5/24 or cur_tot_min > 13/24:
        pinkness = 0
    else:
        pinkness = 1 - abs(1 - (cur_tot_min - 5/24) * 24)
    if pinkness < 0:
        pinkness = 0
    elif pinkness > 1:
        pinkness = 1
    night_shader = [1 - darkness, 1 - darkness, 1 - (0.5 * darkness)]
    sunset_shader = [1, 1 - (0.5 * redness), 1 - redness]
    sunrise_shader = [1, 1 - (0.3 * pinkness), 1 - (0.2 * pinkness)]
    shader = [a * b * c * d for a, b, c, d in zip(preshader, night_shader, \
                                                  sunset_shader, sunrise_shader)]


time_cycle()
day_night_cycle()

chunk = np.array([np.ones((30, 30), dtype=int), \
                  np.random.randint(1, 10, size=(30, 30))])

setup_background()
text_label()



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
    time_cycle()
    day_night_cycle()
    sprites = YAwareGroup(beasts)
    events = pygame.event.get()
    for e in events:
        if e.type == pygame.QUIT:
            running = False
    sprites.update(events, dt)
    setup_background()
    sprites.draw(screen)
    text_label()
    dt = clock.tick(FPS)
    pygame.display.flip()
    for i in beasts:
#        i.safety_behave()
        i.sex_behave()
    
pygame.quit()
