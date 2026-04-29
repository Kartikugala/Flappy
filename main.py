import random  # for generating random numbers
import sys    # We will use sys.exit to sxit the program
from pygame.locals import *  # Basic pygame imports
import pygame

# Global variables for the game
FPS = 32  # Frame Per Second
SCREENWIDTH = 289
SCREENHEIGHT = 511
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
GROUNDY = SCREENHEIGHT * 0.8
GAME_SPRITES = {}
GAME_SOUNDS = {}
PLAYER = 'gallery/sprites/bird.png'
BACKGROUND = 'gallery/sprites/background.png'
PIPE = 'gallery/sprites/pipe.png'


def welcomescreen():
    """
    shows welcome images on the screen
    """
    playerx = int(SCREENWIDTH/5)
    playery = int((SCREENHEIGHT - GAME_SPRITES['player'].get_height())/2)
    messagex = int(
        (SCREENWIDTH - GAME_SPRITES['player'].get_height())/4)  # /2 tha
    messagey = int(SCREENHEIGHT * 0.24)  # .13
    basex = 0
    while True:
        for event in pygame.event.get():
            # if user clicks on cross button then close the game
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

                # if user presses space or up key, start the game for them
            elif event.type == KEYDOWN and (event.key== K_SPACE or event.key == K_UP):
                return
            else:
                SCREEN.blit(GAME_SPRITES['background'], (0, 0))
                SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
                SCREEN.blit(GAME_SPRITES['message'], (messagex, messagey))
                SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
                pygame.display.update()
                FPSCLOCK.tick(FPS)


def maingame():
    score = 0
    playerx = int(SCREENHEIGHT/5)
    playery = int(SCREENHEIGHT/2)
    basex = 0

    # create two pipes for blitting on the screen
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # my list of upperpipe
    upperpipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH/2), 'y': newPipe2[0]['y']}
    ]
    # my list of lowerpipe
    lowerpipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH/2), 'y': newPipe2[1]['y']}
    ]
    
    pipeVelX = -4

    playerVelY = -9
    playerMaxVelY = 10
    playerMinVelY = -8
    playerAccY = 1

    playerFlapAccv = -8  #velocity while flapping
    playerFlapped = False  # It is True only when the bird is flapping

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > 0:
                    playerVelY = playerFlapAccv
                    playerFlapped = True 
                    GAME_SOUNDS['wing'].play()


        crashTest = isCollide(playerx, playery, upperpipes, lowerpipes)  # This function returns True if the player is crashed
        if crashTest:
            return

        # check for Score
        playerMidpos = playerx + GAME_SPRITES['player'].get_width()/2
        for pipe in upperpipes:
            pipeMidpos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width()/2
            if pipeMidpos <= playerMidpos < pipeMidpos + 4:
                score += 1
                print(f"Your Score is {score}")
                GAME_SOUNDS['point'].play()

        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY 

        if playerFlapped:
            playerFlapped = False
        playerHeight = GAME_SPRITES['player'].get_height()
        playery = playery + min(playerVelY, GROUNDY - playery - playerHeight)

        # move pipes to the left 
        for upperpipe , lowerpipe in zip(upperpipes, lowerpipes):
            upperpipe['x'] += pipeVelX 
            lowerpipe['x'] += pipeVelX

        # add a new pipe when the first pipe about to cross the leftmost part of the screen
        if 0<upperpipes[0]['x']<5:
            newpipe = getRandomPipe()
            upperpipes.append(newpipe[0])
            lowerpipes.append(newpipe[1])

        # if the pipe is out of the screen remove it 
        if upperpipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            upperpipes.pop(0)                
            lowerpipes.pop(0)     

        # let's blit our sprites now 
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        for upperpipe , lowerpipe in zip(upperpipes, lowerpipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0], (upperpipe['x'], upperpipe['y'])) 
            SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerpipe['x'], lowerpipe['y'])) 
           
        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))               
        SCREEN.blit(GAME_SPRITES['player'], (playerx, playery)) 
        myDigits = [int(x) for x in list(str(score))]            
        width = 0
        for digit in myDigits:
            width += GAME_SPRITES['numbers'][digit].get_width()
        Xoffset = (SCREENWIDTH - width)/2

        for digit in myDigits:
            SCREEN.blit(GAME_SPRITES['numbers'][digit],(Xoffset, SCREENHEIGHT*0.12))
            Xoffset += GAME_SPRITES['numbers'][digit].get_width()
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def isCollide(playerx, playery, upperpipes, lowerpipes):
    if playery > GROUNDY - 25 or playery < 0:
        GAME_SOUNDS['hit'].play()
        return True
    
    for pipe in upperpipes:
        pipeHeight = GAME_SPRITES['pipe'][0].get_height()
        if(playery < pipeHeight + pipe['y'] and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width()):
            GAME_SOUNDS['hit'].play()
            return True
            
    for pipe in lowerpipes:
        if (playery + GAME_SPRITES['player'].get_height() > pipe['y']) and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width():
            GAME_SOUNDS['hit'].play()
            return True


    return False 

def getRandomPipe():
    """
    Generate positions of two pipe(one bottom and one top rotated )for blitting on the screen 
    """
    pipeHeight = GAME_SPRITES['pipe'][0].get_height()
    offset = SCREENHEIGHT/3
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height() - 1.2*offset))
    y1 = pipeHeight - y2 + offset
    pipeX = SCREENWIDTH + 10
    pipe = [
        {'x': pipeX , 'y':-y1}, # upperpipe
        {'x': pipeX , 'y':y2 }  # lowerpipe
    ]
    return pipe

if __name__ == '__main__':
    # This will be the main point from where are game will start
    pygame.init()  # initialize all pygame modules
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption('Flappy Bird Game')
    GAME_SPRITES['numbers'] = (
        # convert_alpha will change your images pixels and alpha both
        pygame.image.load('gallery/sprites/0.png').convert_alpha(),
        pygame.image.load('gallery/sprites/1.png').convert_alpha(),
        pygame.image.load('gallery/sprites/2.png').convert_alpha(),
        pygame.image.load('gallery/sprites/3.png').convert_alpha(),
        pygame.image.load('gallery/sprites/4.png').convert_alpha(),
        pygame.image.load('gallery/sprites/5.png').convert_alpha(),
        pygame.image.load('gallery/sprites/6.png').convert_alpha(),
        pygame.image.load('gallery/sprites/7.png').convert_alpha(),
        pygame.image.load('gallery/sprites/8.png').convert_alpha(),
        pygame.image.load('gallery/sprites/9.png').convert_alpha(),

    )

    GAME_SPRITES['message'] = pygame.image.load(
        'gallery/sprites/message.png').convert_alpha()
    GAME_SPRITES['base'] = pygame.image.load(
        'gallery/sprites/base.png').convert_alpha()
    GAME_SPRITES['pipe'] = (pygame.transform.rotate(pygame.image.load(PIPE).convert_alpha(), 180),
                            pygame.image.load(PIPE).convert_alpha()
                            )

    # GAME SOUNDS
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('gallery/audio/hit.wav')
    GAME_SOUNDS['die'] = pygame.mixer.Sound('gallery/audio/die.wav')
    GAME_SOUNDS['point'] = pygame.mixer.Sound('gallery/audio/point.wav')
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('gallery/audio/swoosh.wav')
    GAME_SOUNDS['wing'] = pygame.mixer.Sound('gallery/audio/wing.wav')

    GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
    GAME_SPRITES['player'] = pygame.image.load(PLAYER).convert_alpha()

    while True:
        welcomescreen()  # shows welcome screen to the user untill he presses the button0
        maingame()   # this is main game function
