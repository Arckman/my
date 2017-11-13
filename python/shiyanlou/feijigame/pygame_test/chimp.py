
'''
study example for official pygame example chimp(http://www.pygame.org/docs/tut/ChimpLineByLine.html)
'''

#import modules
import os,sys
import pygame
from pygame.locals import *#The special pygame module named “locals” contains constants and functions that have proven useful to put into your program’s global namespace.
if not pygame.font: print ('Warning, fonts disabled')
if not pygame.mixer: print ('Warning, sound disabled')#Some pygame modules are optional, and if they aren’t found, their value is set to “None”.

mypath='/home/fff/.local/lib/python3.5/site-packages/pygame/examples'

#load resources
def load_image(name,colorkey=None):
    '''
    A colorkey is used in graphics to represent a color of the image that is transparent.
    '''
    filename=os.path.join(mypath,'data',name)
    try:
        image=pygame.image.load(filename)
    except pygame.error:
        print('Cannot load image: {}'.format(filename))
        raise SystemExit(str(geterror()))
    image=image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey=image.get_at((0,0))
        image.set_colorkey(colorkey,pygame.locals.RLEACCEL)
    return image,image.get_rect()

def load_sound(name):
    '''
    The first thing this function does is check to see if the pygame.mixer module was imported correctly. If not, it returns a small class instance that has a dummy play method. This will act enough like a normal Sound object for this game to run without any extra error checking.
    '''
    class NoneSound:
        def play(self):pass
    if not pygame.mixer:
        return NoneSound()
    filename=os.path.join(mypath,'data',name)
    try:
        sound=pygame.mixer.Sound(filename)
    except pygame.error:
        print('Cannot load sound: {}'.format(filename))
        raise SystemExit(str(geterror()))
    return sound

class Fist(pygame.sprite.Sprite):
    """moves a clenched fist on the screen, following the mouse"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image,self.rect=load_image('fist.bmp',-1)
        self.punching=0
    
    def update(self):
        pos=pygame.mouse.get_pos()
        self.rect.midtop=pos
        if self.punching:
            self.rect.move_ip(5,10)
    
    def punch(self,target):
        if not self.punching:
            self.punching=1
            hitbox=self.rect.inflate(-5,-5)
            return hitbox.colliderect(target.rect)
    
    def unpunch(self):
        self.punching=0
    
class Chimp(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image,self.rect=load_image('chimp.bmp',-1)
        screen=pygame.display.get_surface()
        self.area=screen.get_rect()
        self.rect.topleft=10,10
        self.move=9
        self.dizzy=0

    def _walk(self):
        newpos=self.rect.move(self.move,0)
        if not self.area.contains(newpos):
            if self.rect.left <self.area.left or self.rect.right>self.area.right:
                self.move=-self.move
                newpos=self.rect.move(self.move,0)
                self.image=pygame.transform.flip(self.image,1,0)
        self.rect=newpos
    
    def _spin(self):
        center=self.rect.center
        self.dizzy+=12
        if self.dizzy>=300:
            self.dizzy=0
            self.image=self.original
        else:
            self.image=pygame.transform.rotate(self.original,self.dizzy)
        self.rect=self.image.get_rect(center=center)

    def update(self):
        if self.dizzy:
            self._spin()
        else:
            self._walk()
    
    def punched(self):
        if not self.dizzy:
            self.dizzy=1
            self.original=self.image

def main():
    #initialize everything
    pygame.init()
    screen=pygame.display.set_mode((468,60))
    pygame.display.set_caption('Monkey Fever')
    pygame.mouse.set_visible(0)

    #create background
    background=pygame.Surface(screen.get_size())
    background=background.convert()
    background.fill((255,255,255))

    #put text on the background and centered
    if pygame.font:
        font=pygame.font.Font(None,36)
        text = font.render("Pummel The Chimp, And Win $$$", 1, (10, 10, 10))
        textpos = text.get_rect(centerx=background.get_width()/2)
        background.blit(text, textpos)

    #display the background when setup finish,black otherwise
    screen.blit(background, (0, 0))
    pygame.display.flip()

    #Prepare Game Object
    whiff_sound = load_sound('whiff.wav')
    punch_sound = load_sound('punch.wav')
    chimp = Chimp()
    fist = Fist()
    allsprites = pygame.sprite.RenderPlain((fist, chimp))
    clock = pygame.time.Clock()

    #main loop
    while True:
        clock.tick(60)

        #handle event
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            elif event.type == MOUSEBUTTONDOWN:
                if fist.punch(chimp):
                    punch_sound.play() #punch
                    chimp.punched()
                else:
                    whiff_sound.play() #miss
            elif event.type == MOUSEBUTTONUP:
                fist.unpunch()
        
        allsprites.update()
    
        #Draw Everything
        screen.blit(background, (0, 0))
        allsprites.draw(screen)
        pygame.display.flip()
    pygame.quit()

if __name__=='__main__':
    main()

