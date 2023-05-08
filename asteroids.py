
#
# Asteroids Game
# 3/ 13/ 2023
# Kitt Starkie
#

# import necessary modules
import pygame
import math
import random

pygame.init()

# define some contants
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

display_height = 600
display_width = 800

player_size = 10
fd_friction = 0.5
bd_friction = 0.1
player_max_speed = 20
player_max_rtsp = 10
bullet_speed = 15
saucer_speed = 5
small_saucer_accuracy = 10

# setup the surface
surface = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Asteroids')
timer = pygame.time.Clock()

# import our sound effects
snd_fire = pygame.mixer.Sound('Sounds/fire.wav')
snd_bangL = pygame.mixer.Sound('Sounds/bangLarge.wav')
snd_bangM = pygame.mixer.Sound('Sounds/bangMedium.wav')
snd_bangS = pygame.mixer.Sound('Sounds/bangSmall.wav')
snd_extra = pygame.mixer.Sound('Sounds/extra.wav')
snd_saucerB = pygame.mixer.Sound('Sounds/saucerBig.wav')
snd_saucerS = pygame.mixer.Sound('Sounds/saucerSmall.wav')
snd_thrust = pygame.mixer.Sound('Sounds/thrust.wav')

# create a function for displaying text
def drawText(message, color, x, y, s, center=True):
    screen_text = pygame.font.SysFont('Calibri', s).render(message, True, color)
    if center == True:
        rect = screen_text.get_rect()
        rect.center = (x,y)
    else:
        rect = (x,y)    
    surface.blit(screen_text, rect)
       

# create a function to check for collision
def isColliding(x,y,xTo,yTo,size):
    if x > xTo - size and x < xTo + size and y > yTo - size and y < yTo + size:
        return True
    return False

# define the asteroid sprite
class Asteroid:
    def __init__(self, x, y, t):
        self.x = x
        self.y = y
       
        if t == 'Large':
            self.size = 30
        elif t == 'Normal':
            self.size = 20
        else:
            self.size = 10
       
        self.t = t
       
        # make the initial direction and speed random
        self.speed = random.uniform(1, (40-self.size) * 4/15)
        # pick a direction and convert to radians
        self.dir = random.randrange(0, 360) * math.pi/180

        # make the data structure that will hold the vertices of the asteroid
        full_circle = random.uniform(18,36)
        dist = random.uniform(self.size/2, self.size)
        self.vertices = []
        while full_circle < 360:
            self.vertices.append([dist, full_circle])
            dist = random.uniform(self.size/2, self.size)
            full_circle += random.uniform(18,36)

    def updateAsteroid(self):
        # Move asteroid
        self.x += self.speed * math.cos(self.dir)
        self.y += self.speed * math.sin(self.dir)

        # Check for wrapping
        if self.x > display_width:
            self.x = 0
        elif self.x < 0:
            self.x = display_width
        elif self.y > display_height:
            self.y = 0
        elif self.y < 0:
            self.y = display_height

        # Draw asteroid
        for v in range(len(self.vertices)):
            if v == len(self.vertices) - 1:
                next_v = self.vertices[0]
            else:
                next_v = self.vertices[v + 1]
            this_v = self.vertices[v]
            pygame.draw.line(surface, WHITE, (self.x + this_v[0] * math.cos(this_v[1] * math.pi / 180),
                                                  self.y + this_v[0] * math.sin(this_v[1] * math.pi / 180)),
                             (self.x + next_v[0] * math.cos(next_v[1] * math.pi / 180),
                              self.y + next_v[0] * math.sin(next_v[1] * math.pi / 180)))
# create class to model the destroyed player
class deadPlayer:
    def __init__(self,x,y,l):
        self.angle = random.randrange(0, 360) * math.pi / 180
        self.dir = random.randrange(0, 360) * math.pi / 180
       
        self.rtspd = random.uniform(-0.25,0.25)
        self.x = x
        self.y = y
        self.lenght = l
        self.speed = random.randint(2,8)
    def updateDeadPlayer(self):
        pygame.draw.line(surface, WHITE,
                         (self.x + self.lenght * math.cos(self.angle) / 2,
                          self.y + self.lenght * math.sin(self.angle) / 2),
                         (self.x - self.lenght * math.cos(self.angle) / 2,
                          self.y - self.lenght * math.sin(self.angle) / 2))
        self.angle += self.rtspd
        self.x += self.speed * math.cos(self.dir)
        self.y += self.speed * math.sin(self.dir)
       

# define the player sprite
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hspeed = 0
        self.vspeed = 0
        self.dir = -90
        self.thrust = False
        self.rtspd = 0
       
    def updatePlayer(self):
        # Move player
        speed = math.sqrt(self.hspeed**2 + self.vspeed**2)
        if self.thrust:
            if speed + fd_friction < player_max_speed:
                self.hspeed += fd_friction * math.cos(self.dir * math.pi / 180)
                self.vspeed += fd_friction * math.sin(self.dir * math.pi / 180)
            else:
                self.hspeed = player_max_speed * math.cos(self.dir * math.pi / 180)
                self.vspeed = player_max_speed * math.sin(self.dir * math.pi / 180)
        else:
            if speed - bd_friction > 0:
                change_in_hspeed = (bd_friction * math.cos(self.vspeed / self.hspeed))
                change_in_vspeed = (bd_friction * math.sin(self.vspeed / self.hspeed))
                if self.hspeed != 0:
                    if change_in_hspeed / abs(change_in_hspeed) == self.hspeed / abs(self.hspeed):
                        self.hspeed -= change_in_hspeed
                    else:
                        self.hspeed += change_in_hspeed
                if self.vspeed != 0:
                    if change_in_vspeed / abs(change_in_vspeed) == self.vspeed / abs(self.vspeed):
                        self.vspeed -= change_in_vspeed
                    else:
                        self.vspeed += change_in_vspeed
            else:
                self.hspeed = 0
                self.vspeed = 0
        self.x += self.hspeed
        self.y += self.vspeed

        # Check for wrapping
        if self.x > display_width:
            self.x = 0
        elif self.x < 0:
            self.x = display_width
        elif self.y > display_height:
            self.y = 0
        elif self.y < 0:
            self.y = display_height

        # Rotate player
        self.dir += self.rtspd

    def drawPlayer(self):
        a = math.radians(self.dir)
        x = self.x
        y = self.y
        s = player_size
        t = self.thrust
       
        # draw the player using pygame
        pygame.draw.line(surface, WHITE,
                         (x - (s * math.sqrt(130) / 12) * math.cos(math.atan(7 / 9) + a),
                          y - (s * math.sqrt(130) / 12) * math.sin(math.atan(7 / 9) + a)),
                         (x + s * math.cos(a), y + s * math.sin(a)))

        pygame.draw.line(surface, WHITE,
                         (x - (s * math.sqrt(130) / 12) * math.cos(math.atan(7 / 9) - a),
                          y + (s * math.sqrt(130) / 12) * math.sin(math.atan(7 / 9) - a)),
                         (x + s * math.cos(a), y + s * math.sin(a)))

        pygame.draw.line(surface, WHITE,
                         (x - (s * math.sqrt(2) / 2) * math.cos(a + math.pi / 4),
                          y - (s * math.sqrt(2) / 2) * math.sin(a + math.pi / 4)),
                         (x - (s * math.sqrt(2) / 2) * math.cos(-a + math.pi / 4),
                          y + (s * math.sqrt(2) / 2) * math.sin(-a + math.pi / 4)))
        if t:
            pygame.draw.line(surface, WHITE,
                             (x - s * math.cos(a),
                              y - s * math.sin(a)),
                             (x - (s * math.sqrt(5) / 4) * math.cos(a + math.pi / 6),
                              y - (s * math.sqrt(5) / 4) * math.sin(a + math.pi / 6)))
            pygame.draw.line(surface, WHITE,
                             (x - s * math.cos(-a),
                              y + s * math.sin(-a)),
                             (x - (s * math.sqrt(5) / 4) * math.cos(-a + math.pi / 6),
                              y + (s * math.sqrt(5) / 4) * math.sin(-a + math.pi / 6)))
       
    def killPlayer(self):
        # reset the player
        self.x = display_width/2
        self.y = display_height/2
        self.thrust = False
        self.dir = -90
        self.hspeed = 0
        self.vspeed = 0

# define a bullet used by all objects on the screen
class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.dir = direction
        self.life = 30
    def updateBullet(self):
        # Moving
        self.x += bullet_speed * math.cos(self.dir * math.pi / 180)
        self.y += bullet_speed * math.sin(self.dir * math.pi / 180)

        # Drawing
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), 3)

        # Wrapping
        if self.x > display_width:
            self.x = 0
        elif self.x < 0:
            self.x = display_width
        elif self.y > display_height:
            self.y = 0
        elif self.y < 0:
            self.y = display_height
        self.life -= 1
   
class Saucer:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.state = 'Dead'
        self.type = 'Large'
        self.dirchoice = ()
        self.bullets = []
        self.cd = 0
        self.bdir = 0
       
    def updateSaucer(self):
        # Move player
        self.x += saucer_speed * math.cos(self.dir * math.pi / 180)
        self.y += saucer_speed * math.sin(self.dir * math.pi / 180)

        # Choose random direction
        if random.randrange(0, 100) == 1:
            self.dir = random.choice(self.dirchoice)

        # Wrapping
        if self.y < 0:
            self.y = display_height
        elif self.y > display_height:
            self.y = 0
        if self.x < 0 or self.x > display_width:
            self.state = "Dead"

        # Shooting
        if self.type == "Large":
            self.bdir = random.randint(0, 360)
        if self.cd == 0:
            self.bullets.append(Bullet(self.x, self.y, self.bdir))
            self.cd = 30
        else:
            self.cd -= 1
   
    def createSaucer(self):
        # Create saucer
        # Set state
        self.state = "Alive"

        # Set random position
        self.x = random.choice((0, display_width))
        self.y = random.randint(0, display_height)

        # Set random type
        if random.randint(0, 1) == 0:
            self.type = "Large"
            self.size = 20
        else:
            self.type = "Small"
            self.size = 10

        # Create random direction
        if self.x == 0:
            self.dir = 0
            self.dirchoice = (0, 45, -45)
        else:
            self.dir = 180
            self.dirchoice = (180, 135, -135)

        # Reset bullet cooldown
        self.cd = 0
           
    def drawSaucer(self):
        # Draw saucer
        pygame.draw.polygon(surface, WHITE,
                            ((self.x + self.size, self.y),
                             (self.x + self.size / 2, self.y + self.size / 3),
                             (self.x - self.size / 2, self.y + self.size / 3),
                             (self.x - self.size, self.y),
                             (self.x - self.size / 2, self.y - self.size / 3),
                             (self.x + self.size / 2, self.y - self.size / 3)), 1)
        pygame.draw.line(surface, WHITE,
                         (self.x - self.size, self.y),
                         (self.x + self.size, self.y))
        pygame.draw.polygon(surface, WHITE,
                            ((self.x - self.size / 2, self.y - self.size / 3),
                             (self.x - self.size / 3, self.y - 2 * self.size / 3),
                             (self.x + self.size / 3, self.y - 2 * self.size / 3),
                             (self.x + self.size / 2, self.y - self.size / 3)), 1)
   
# define main game loop
def gameLoop(startingState):
    # initialize game loop variable
    gameState = startingState
    playerState = 'Alive'
    player_pieces = []
    bullet_capacity = 4
    asteroids = []
    bullets = []
    stage = 3
    score = 0
    lives = 2
    player = Player(display_width/2, display_height/2)
    saucer = Saucer()
   
   
    while gameState != 'Exit':
        # initial game menu
        while gameState == 'Menu':
            surface.fill(BLACK)
            drawText('ASTEROIDS!', WHITE, display_width/2, display_height/2, 100)
            drawText('press any key to START', WHITE, display_width/2, display_height/2 + 100, 50)
           
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    gameState = 'exit'
                if event.type == pygame.KEYDOWN:
                    gameState = 'playing'
                   
                pygame.display.update()
       
        # here we are going to process all the events associated with playing the game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameState = 'Exit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player.thrust = True
                if event.key == pygame.K_LEFT:
                    player.rtspd = -player_max_rtsp
                if event.key == pygame.K_RIGHT:
                    player.rtspd = player_max_rtsp
                if event.key == pygame.K_SPACE and len(bullets) < bullet_capacity:
                    bullets.append(Bullet(player.x, player.y, player.dir))
                if gameState == "Game over":
                    if event.key == pygame.K_r:
                        gameState = "Exit"
                        gameLoop('Playing')
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    player.thrust = False
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    player.rtspd = 0
               
       
# update and move the player
        player.updatePlayer()
               
        # reset the display
        surface.fill(BLACK)
           
        # check for asteroid collisions
        for a in asteroids:
            a.updateAsteroid()

            # add code for collisions later
            if playerState != "Died":
                if isColliding(player.x,player.y,a.x,a.y,a.size):
                    # Create the ship fragments
                    player_pieces.append(deadPlayer(player.x, player.y, 5 * player_size / (2*math.cos(math.atan(1/3)))))
                    player_pieces.append(deadPlayer(player.x, player.y, 5 * player_size / (2*math.cos(math.atan(1/3)))))
                    player_pieces.append(deadPlayer(player.x, player.y, player_size))
                    # kill the player, there was a collision
                    player.state = "Died"
                    player.killPlayer()
                   
                    if lives != 0:
                        lives-=1
                    else:
                        gameState = "Game over"
                   
                    # Split asteroid
                    if a.t == "Large":
                        asteroids.append(Asteroid(a.x, a.y, "Normal"))
                        asteroids.append(Asteroid(a.x, a.y, "Normal"))
                        score += 20
                        # Play SFX
                        pygame.mixer.Sound.play(snd_bangL)
                    elif a.t == "Normal":
                        asteroids.append(Asteroid(a.x, a.y, "Small"))
                        asteroids.append(Asteroid(a.x, a.y, "Small"))
                        score += 50
                        # Play SFX
                        pygame.mixer.Sound.play(snd_bangM)
                    else:
                        score += 100
                        # Play SFX
                        pygame.mixer.Sound.play(snd_bangS)
                   
                    asteroids.remove(a)
                                   
        # Changes after this point
        for f in player_pieces:
            f.updateDeadPlayer()
            if f.x > display_width or f.x < 0 or f.y > display_height or f.y < 0:
                player_pieces.remove(f)
               
        # start the game or advance to a new level
        if len(asteroids) == 0:
            stage += 1
            # spawn the asteroids away from the middle
            for i in range(stage):
                xTo = display_width/2
                yTo = display_height/2

                # recalculate the xto and yto so that they don't spawn in the middle of the screen
                while xTo - display_width/2 < display_width/4 and yTo - display_height/2 < display_height/4:
                    xTo = random.randrange(0, display_width)
                    yTo = random.randrange(0, display_height)
                   
                asteroids.append(Asteroid(xTo,yTo,'Large'))
       
        # create the saucer
        if saucer.state == 'Dead':
            saucer.createSaucer()
        else:
            acc = small_saucer_accuracy * 4 / stage
            saucer.bdir = math.degrees(math.atan2(-saucer.y + player.y,-saucer.x + player.x) + math.radians(random.uniform(acc, -acc)))
           
            saucer.updateSaucer()
            saucer.drawSaucer()
           
            # Check for collision w/ asteroid
            for a in asteroids:
                if isColliding(saucer.x, saucer.y, a.x, a.y, a.size + saucer.size):
                    # Set saucer state
                    saucer.state = "Dead"

                    # Split asteroid
                    if a.t == "Large":
                        asteroids.append(Asteroid(a.x, a.y, "Normal"))
                        asteroids.append(Asteroid(a.x, a.y, "Normal"))
                        # Play SFX
                        pygame.mixer.Sound.play(snd_bangL)
                    elif a.t == "Normal":
                        asteroids.append(Asteroid(a.x, a.y, "Small"))
                        asteroids.append(Asteroid(a.x, a.y, "Small"))
                        # Play SFX
                        pygame.mixer.Sound.play(snd_bangM)
                    else:
                        # Play SFX
                        pygame.mixer.Sound.play(snd_bangS)
                    asteroids.remove(a)

            # check for collisions with player bullets
            for b in bullets:
                if isColliding(b.x,b.y,saucer.x,saucer.y,saucer.size):
                    # add points
                    if saucer.type == "Large":
                        score += 200
                    else:
                        score += 1000
                    saucer.state = "Dead"
                    pygame.mixer.Sound.play(snd_bangL)
                    bullets.remove(b)
            if isColliding(saucer.x,saucer.y,player.x,player.y,saucer.size):
                if playerState != "Died":
                    player_pieces.append(deadPlayer(player.x, player.y, 5 * player_size / (2*math.cos(math.atan(1/3)))))
                    player_pieces.append(deadPlayer(player.x, player.y, 5 * player_size / (2*math.cos(math.atan(1/3)))))
                    player_pieces.append(deadPlayer(player.x, player.y, player_size))                                        
                   
                    # Kill the player as there has been a collision
                    player_state = 'Died'
                    player.killPlayer()
                   
                    if lives != 0:
                        lives -= 1
                    else:
                        gameState = 'Game Over'
                       
                    pygame.mixer.Sound.play(snd_bangL)
           
            # check for collisions with saucer bullets
                for b in saucer.bullets:
                    b.updateBullet()
                    for a in asteroids:
                        if isColliding(b.x, b.y, a.x, a.y, a.size):
                            # Split asteroid
                            if a.t == "Large":
                                asteroids.append(Asteroid(a.x, a.y, "Normal"))
                                asteroids.append(Asteroid(a.x, a.y, "Normal"))
                                # Play SFX
                                pygame.mixer.Sound.play(snd_bangL)
                            elif a.t == "Normal":
                                asteroids.append(Asteroid(a.x, a.y, "Small"))
                                asteroids.append(Asteroid(a.x, a.y, "Small"))
                                # Play SFX
                                pygame.mixer.Sound.play(snd_bangL)
                            else:
                                # Play SFX
                                pygame.mixer.Sound.play(snd_bangL)
                            # Remove asteroid and bullet
                            asteroids.remove(a)
                            saucer.bullets.remove(b)

                            break
            # check for collisions between player and saucer bullets
                if isColliding(player.x, player.y, b.x, b.y, 5):
                    if player_state != "Died":
                        # Create ship fragments
                        player_pieces.append(deadPlayer(player.x, player.y, 5 * player_size / (2 * math.cos(math.atan(1 / 3)))))
                        player_pieces.append(deadPlayer(player.x, player.y, 5 * player_size / (2 * math.cos(math.atan(1 / 3)))))
                        player_pieces.append(deadPlayer(player.x, player.y, player_size))

                        # Kill player
                        player_state = "Died"
                        player_dying_delay = 30
                        player_invi_dur = 120
                        player.killPlayer()
                        
                        if live != 0:
                            live -= 1
                        else:
                            gameState = "Game Over"

                        # Play SFX
                        pygame.mixer.Sound.play(snd_bangL)

                        # Remove bullet
                        saucer.bullets.remove(b)

                if b.life <= 0 and b in saucer.bullets:
                    saucer.bullets.remove(b)
       
        # create and check for collisions
        for b in bullets:
            b.updateBullet()                
            # here we are checking for bullets hitting asteroids
            for a in asteroids:
                if b.x > a.x - a.size and b.x < a.x + a.size and b.y > a.y - a.size and b.y < a.y + a.size:
                    # this is a collision - split the asteroid
                    if a.t == 'Large':
                        asteroids.append(Asteroid(a.x,a.y,'Normal'))
                        asteroids.append(Asteroid(a.x,a.y,'Normal'))
                        score += 20
                        pygame.mixer.Sound.play(snd_bangL)
                    elif a.t == 'Normal':
                        asteroids.append(Asteroid(a.x,a.y,'Small'))
                        asteroids.append(Asteroid(a.x,a.y,'Small'))
                        score += 50
                        pygame.mixer.Sound.play(snd_bangM)

                    else:
                        score += 100
                        pygame.mixer.Sound.play(snd_bangS)

                    asteroids.remove(a)
                    bullets.remove(b)
                   
                    break
                   
                # expire bullets
            if b.life <= 0:
                bullets.remove(b)
               
        if gameState != "Game over":
            if playerState == 'Died':
                pass
            else:
                player.drawPlayer()
        else:
            drawText('Game Over', WHITE, display_width/2, display_height/2, 100)
            drawText('Press R to restart', WHITE, display_width/2, display_height/2+100,50)
            lives = -1

        
        # draw the score
        drawText(str(score), WHITE, 60, 20, 40, False)
        
        # draw how many lives we have
        for l in range(lives + 1):
            Player(75+l*25, 75).drawPlayer()
           
        pygame.display.update()
        timer.tick(30)
           
# start the game loop
gameLoop('Menu')
pygame.quit()