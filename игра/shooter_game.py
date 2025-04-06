import pygame
from pygame import *
from random import randint
from pygame.font import Font
from time import time as timer

# Initialize Pygame
pygame.init()

# Window settings
window = display.set_mode((700, 500))
display.set_caption("Shooter Game")
background = transform.scale(image.load("galaxy.jpg"), (700, 500))

# Load sounds
mixer.init()
mixer.music.load('space.ogg')  # Ensure the space.ogg file exists
fire_sound = mixer.Sound('fire.ogg')  # Ensure the fire.ogg file exists
mixer.music.play(-1)

# Define classes
class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, player_speed=0):
        super().__init__()
        self.image = transform.scale(image.load(player_image), (65, 65))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))


class Player(GameSprite):
    def __init__(self, player_image, player_x, player_y, player_speed):
        super().__init__(player_image, player_x, player_y, player_speed)

    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT]:
            self.rect.x -= self.speed
        if keys[K_RIGHT]:
            self.rect.x += self.speed

        # Boundary limits for the player
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > 700:
            self.rect.right = 700


class Enemy(GameSprite):
    def __init__(self, player_image, player_x, player_y):
        super().__init__(player_image, player_x, player_y, randint(1, 4))

    def update(self):
        global lost
        if self.rect.top > 500:
            lost += 1
            self.rect.x = randint(5, 635)
            self.rect.y = -65

        self.rect.y += self.speed


class Bullet(GameSprite):
    def __init__(self, player_image, player_x, player_y):
        super().__init__(player_image, player_x, player_y, 10)

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()  # Remove bullet if it goes off-screen


class Asteroid(GameSprite):
    def __init__(self, player_image, player_x, player_y):
        super().__init__(player_image, player_x, player_y, randint(1, 4))

    def update(self):
        global lost
        if self.rect.top > 500:
            lost += 1
            self.rect.x = randint(5, 635)
            self.rect.y = -65

        self.rect.y += self.speed


# Game setup
rocket = Player('rocket.png', 300, 440, 5)  # Make sure 'rocket.png' exists
bullets = sprite.Group()
enemies = sprite.Group()
asteroids = sprite.Group()

for i in range(5):
    enemy = Enemy('ufo.png', randint(5, 635), -65)  # Ensure 'ufo.png' exists
    enemies.add(enemy)

for i in range(3):
    asteroid = Asteroid('asteroid.png', randint(5, 635), -40)  # Ensure 'asteroid.png' exists
    asteroids.add(asteroid)

# Game state variables
score = 0
lost = 0
life = 3
font = Font(None, 36)
run = True
rel_time = False
num_fire = 0
clock = time.Clock()

while run:
    for e in event.get():
        if e.type == QUIT:
            run = False
        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                if num_fire < 5 and not rel_time:
                    num_fire += 1
                    fire_sound.play()
                    bullet = Bullet('bullet.png', rocket.rect.centerx, rocket.rect.top)  # Ensure 'bullet.png' exists
                    bullets.add(bullet)
                if num_fire >= 5 and not rel_time:
                    last_time = timer()
                    rel_time = True

    window.blit(background, (0, 0))
    rocket.update()
    rocket.reset()

    # Update and draw enemies
    enemies.update()
    enemies.draw(window)

    # Update and draw bullets
    bullets.update()
    bullets.draw(window)

    # Update and draw asteroids
    asteroids.update()
    asteroids.draw(window)

    if rel_time:
        now_time = timer()
        if now_time - last_time < 3:
            reload_text = font.render('Wait, reloading...', True, (150, 0, 0))
            window.blit(reload_text, (260, 460))
        else:
            num_fire = 0
            rel_time = False

    # Check for collisions
    collides = sprite.groupcollide(bullets, enemies, True, True)
    for collide in collides:
        score += 1
        enemy = Enemy('ufo.png', randint(5, 635), -65)
        enemies.add(enemy)

    # Check if player collides with enemies or asteroids
    if sprite.spritecollide(rocket, enemies, False) or sprite.spritecollide(rocket, asteroids, False):
        sprite.spritecollide(rocket, enemies, True)
        sprite.spritecollide(rocket, asteroids, True)
        life -= 1
        if life <= 0:
            run = False

    # Draw score, lives, and lost
    score_text = font.render("Score: " + str(score), True, (255, 255, 255))
    window.blit(score_text, (10, 10))
    
    lost_text = font.render("Missed: " + str(lost), True, (255, 255, 255))
    window.blit(lost_text, (10, 40))
    
    life_text = font.render("Lives: " + str(life), True, (255, 255, 255))
    window.blit(life_text, (10, 70))

    # Check for game over or win conditions
    if lost >= 20 or life <= 0:
        game_over_text = font.render("GAME OVER", True, (255, 0, 0))
        window.blit(game_over_text, (250, 250))
        run = False

    if score >= 10:
        win_text = font.render("YOU WIN!", True, (62, 240, 0))
        window.blit(win_text, (250, 250))
        run = False

    display.update()
    clock.tick(60)

pygame.quit()                          