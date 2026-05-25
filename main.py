import pygame
import sys

# ==========================================
# 1. INITIALIZATION & CONSTANTS
# ==========================================
pygame.init()

# Screen dimensions
#C Adjusting the dimensions should also adjust all elements to scale  it
#C Also assuming the board is 24x12
WIDTH = 960
HEIGHT = WIDTH/2
TILE_SIZE = WIDTH/24
FPS = 60

# Colors (Students can change these!)
#C *Made some colors I used less harsh
BLACK = (0, 0, 0)
WHITE = (240, 230, 244)
BLUE = (0, 0, 255)
C_RED = (255, 50, 50)
GREEN = (0, 255, 0)
YELLOW = (255, 240, 0)
PURPLE = (180, 20, 255)
C_BLUE = (40, 40, 225)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Explorer - Student Edition - C")
clock = pygame.time.Clock()

# ==========================================
# 2. SPRITE CLASSES
# ==========================================
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # To use an image later: self.image = pygame.image.load("player.png")
        self.image = pygame.Surface((TILE_SIZE*3/4, TILE_SIZE*3/4))
        self.image.fill(C_BLUE)
        self.rect = self.image.get_rect()

        # Save starting position for when the player dies
        self.start_x = x * TILE_SIZE * 1.125
        self.start_y = y * TILE_SIZE * 1.125
        self.rect.x = self.start_x
        self.rect.y = self.start_y

        self.speed = TILE_SIZE/10
        self.facing = "RIGHT" # Helps bullets know which way to go

    def update(self, walls):
        # Save old position in case we hit a wall
        old_x = self.rect.x
        old_y = self.rect.y

        keys = pygame.key.get_pressed()

        # ==========================================
        # STUDENT TODO 1: PLAYER MOVEMENT
        # ==========================================
        # Hint: If the left arrow key is pressed (pygame.K_LEFT),
        # decrease self.rect.x by self.speed and set self.facing to "LEFT".
        # Do the same for RIGHT, UP, and DOWN!

        # [WRITE YOUR MOVEMENT CODE HERE]
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.rect.x = self.rect.x - self.speed
                self.facing = "LEFT"
            if event.key == pygame.K_RIGHT:
                self.rect.x = self.rect.x + self.speed
                self.facing = "RIGHT"
            if event.key == pygame.K_UP:
                self.rect.y = self.rect.y - self.speed
                self.facing = "UP"
            if event.key == pygame.K_DOWN:
                self.rect.y= self.rect.y + self.speed
                self.facing = "DOWN"

        # --- Wall Collision Logic (Provided so you don't get stuck!) ---
        # If the player hits a wall after moving, we push them back to their old position.
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                self.rect.x = old_x
                self.rect.y = old_y

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(PURPLE)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE*3/4, TILE_SIZE*3/4))
        self.image.fill(C_RED)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE * 1.125
        self.rect.y = y * TILE_SIZE * 1.125
        self.move_timer = 0
        self.direction = 1

    #C Updated enemy movement to also scale on their speed/tile size
    def update(self):
        # Simple enemy movement: wobble back and forth
        self.move_timer += 1
        if self.move_timer > 30:
            self.direction *= -1
            self.move_timer = 0
        self.rect.y += self.direction * TILE_SIZE/20 

class Goal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = TILE_SIZE/4
        self.direction = direction

    def update(self):
        if self.direction == "RIGHT":
            self.rect.x += self.speed
        elif self.direction == "LEFT":
            self.rect.x -= self.speed
        elif self.direction == "UP":
            self.rect.y -= self.speed
        elif self.direction == "DOWN":
            self.rect.y += self.speed

        # Kill bullet if it goes off screen to save memory
        if self.rect.right < 0 or self.rect.left > WIDTH or self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()

# ==========================================
# 3. LEVEL DESIGN (Highly Customizable)
# ==========================================
# W = Wall, P = Player Start, E = Enemy, G = Goal, Space = Empty
#C Adjusted level, and changed it to be 24 by 12
level_map = [
    "WWWWWWWWWWWWWWWWWWWWWWWW",
    "WP    W           E    W",
    "W     W    W   E  W    W",
    "W     W    W      WE   W",
    "W  E  W E  W E    W    W",
    "W          W    WWW    W",
    "W          W      WE   W",
    "W E  WWWWWWWWWWWE W    W",
    "W    W      W          W",
    "W    W   W  W      W   W",
    "W        W         W   G",
    "WWWWWWWWWWWWWWWWWWWWWWWW",
]

# Sprite Groups
all_sprites = pygame.sprite.Group()
walls = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
goals = pygame.sprite.Group()

player = None

# Parse the level map
for row_index, row in enumerate(level_map):
    for col_index, char in enumerate(row):
        if char == "W":
            wall = Wall(col_index, row_index)
            all_sprites.add(wall)
            walls.add(wall)
        elif char == "P":
            player = Player(col_index, row_index)
            all_sprites.add(player)
        elif char == "E":
            enemy = Enemy(col_index, row_index)
            all_sprites.add(enemy)
            enemies.add(enemy)
        elif char == "G":
            goal = Goal(col_index, row_index)
            all_sprites.add(goal)
            goals.add(goal)

# ==========================================
# 4. MAIN GAME LOOP
# ==========================================
running = True
while running:
    # --- Events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # ==========================================
                # STUDENT TODO 2: SHOOTING
                # ==========================================
                # When SPACE is pressed, create a Bullet object.
                # Pass it the player's center x, center y, and facing direction.
                # Add the new bullet to 'all_sprites' and 'bullets' groups.

                # [WRITE YOUR SHOOTING CODE HERE]
                bullet = Bullet(player.rect.centerx, player.rect.centery, player.facing)
                all_sprites.add(bullet)
                bullets.add(bullet)

    # --- Updates ---
    # Update player (passing walls for collision check)
    player.update(walls)

    # Update other sprites
    enemies.update()
    bullets.update()

    # ==========================================
    # STUDENT TODO 3: BULLET VS ENEMY COLLISION
    # ==========================================
    # Hint: Use pygame.sprite.groupcollide(group1, group2, dokill1, dokill2)
    # If a bullet hits an enemy, BOTH should disappear (dokill=True).

    # [WRITE YOUR BULLET COLLISION CODE HERE]
    #C Bullets should be destroyed on collision with enemies and walls
    pygame.sprite.groupcollide(bullets, enemies, True, True)
    pygame.sprite.groupcollide(bullets, walls, True, False)
    # ==========================================
    # STUDENT TODO 4: PLAYER VS ENEMY COLLISION
    # ==========================================
    # Hint: Use pygame.sprite.spritecollide(sprite, group, dokill)
    # If the player hits an enemy, teleport the player back to player.start_x and player.start_y.

    # [WRITE YOUR ENEMY COLLISION CODE HERE]
    player_die = pygame.sprite.spritecollide(player, enemies, False)

    if player_die:
        player.rect.x = player.start_x
        player.rect.y = player.start_y

    # ==========================================
    # STUDENT TODO 5: WIN CONDITION (PLAYER VS GOAL)
    # ==========================================
    # If the player collides with the goal, print "YOU WIN!" to the console and set running = False

    # [WRITE YOUR WIN CONDITION CODE HERE]
    player_win = pygame.sprite.spritecollide(player, goals, False)
    if player_win:
        print("YOU WIN")
        running = False

    # --- Drawing ---
    screen.fill(BLACK)
    all_sprites.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
