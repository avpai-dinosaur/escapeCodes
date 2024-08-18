import pygame
import utils
import constants as c
import objects as o
import random
import math
from spritesheet import SpriteSheet
from enum import Enum

class Enemy(pygame.sprite.Sprite):
    """Represents an enemy."""

    class MoveState(Enum):
        """State of the enemy's movement."""
        PATH = 0
        CHASE = 1
        RECOVER = 2

    def __init__(self, image, path):
        """Constructor.

            path: List of Vector2 objects specifying path along 
                  which the enemy will walk.
            image: enemy sprite PNG file.
        """
        super().__init__()

        # Animation Variables
        self.spritesheet = SpriteSheet(image, c.ENEMY_SHEET_METADATA)
        self.action = "walk"
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.cooldown = 100
        
        # Image variables
        self.image = self.spritesheet.get_image(self.action, self.current_frame)
        self.rect = self.image.get_rect()
        self.face_right = True

        # Path following
        self.route = None
        self.path = path
        self.pos = self.path[0].copy() # This NEEDS to be a copy to avoid modifying path!
        self.rect.center = self.pos
        self.target_point = 1
        self.target = self.path[self.target_point]
        self.direction = 1

        self.move_state = Enemy.MoveState.PATH
        self.radius = 50

        # Enemy characteristics
        self.health = o.EnemyHealthBar(self.rect.left, self.rect.top, 60, 10, 100)
        self.melee_lose_cooldown = 200
        self.last_melee_hit = pygame.time.get_ticks()
        self.speed = c.ENEMY_SPEED
    
    def get_route(self, route):
        r = []
        for node in route:
            row = node // c.MAP_WIDTH
            col = node - row * c.MAP_WIDTH
            r.append(pygame.rect.Rect(
                col * c.TILE_SIZE,
                row * c.TILE_SIZE,
                c.TILE_SIZE,
                c.TILE_SIZE
            ))
        return r

    def update(self, player, bullets, map):
        """Update function to run each game tick.
        
        Enemy should move randomly and reverse direction if it bounces off a wall.

            walls: list of pygame.Rects representing walls in the map.
        """
        tile_y = int(self.pos.y // c.TILE_SIZE)
        tile_x = int(self.pos.x // c.TILE_SIZE)
        my_node = tile_y * c.MAP_WIDTH + tile_x

        target_node = int(player.pos.y // c.TILE_SIZE) * c.MAP_WIDTH + int(player.pos.x // c.TILE_SIZE)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_f]:
            dist, prev = map.graph.dijkstra(my_node, target_node)

            route = []
            node = target_node
            while node:
                route.append(node)
                node = prev[node]
            self.route = self.get_route(route)
        

        # if self.move_state == Enemy.MoveState.PATH:
        #     self.pathmove(walls)
        # elif self.move_state == Enemy.MoveState.CHASE:
        #     self.chasemove(player, walls)
        # else:
        #     self.recovermove(walls)

        # if pygame.sprite.collide_circle(player, self):
        #     self.move_state = Enemy.MoveState.CHASE
        #     self.speed = c.ENEMY_CHASE_SPEED
        # else:
        #     if self.move_state == Enemy.MoveState.CHASE:
        #         self.move_state = Enemy.MoveState.RECOVER
        #         self.speed = c.ENEMY_SPEED
        
        # # receive hits from player
        # if pygame.Rect.colliderect(player.rect, self.rect) and player.action == "punch":
        #     if pygame.time.get_ticks() - self.last_melee_hit > self.melee_lose_cooldown:
        #         self.last_melee_hit = pygame.time.get_ticks()
        #         self.health.lose(2)
        
        # # receive hits from bullets
        # hit_bullet = pygame.sprite.spritecollideany(self, bullets)
        # if hit_bullet:
        #     hit_bullet.kill()
        #     self.health.lose(hit_bullet.damage)

        # if self.health.hp <= 0:
        #     self.kill()
            
        # self.update_animation()

    def update_animation(self):
        """Update animation of enemy."""
        current_time = pygame.time.get_ticks()
        if(current_time - self.last_update >= self.cooldown):
            #if animation cooldown has passed between last update and current time, switch frame
            self.current_frame += 1
            self.last_update = current_time
            
            #reset frame back to 0 so it doesn't index out of bounds
            if(self.current_frame >= self.spritesheet.num_frames(self.action)):
                self.current_frame = 0
            
            self.image = pygame.transform.flip(
                self.spritesheet.get_image(self.action, self.current_frame), 
                self.face_right,
                False
            )

    def pathmove(self, walls):
        """Move the enemy towards next path point.
        
        Enemy should reverse direction upon reaching either end of path.
        """
        if self.move(self.target, walls):
            if self.target_point == len(self.path) - 1 or self.target_point == 0:
                self.direction *= -1
                self.face_right = not self.face_right
            self.target_point += self.direction
            self.target = self.path[self.target_point]
    
    def chasemove(self, player, walls):
        """Chase the player."""
        self.move(player.pos, walls)
    
    def recovermove(self, walls):
        """Recover back to patrol."""
        if self.move(self.target, walls):
            self.move_state = Enemy.MoveState.PATH

    def move(self, target, walls):
        """Move enemy to the target point.

        Returns true if target was reached.
        
            target: Vector2.
        """
        old_pos = self.pos.copy()
        reached = False
        movement = target - self.pos
        distance = movement.length()

        if movement[0] < 0:
            self.face_right = False
        elif movement[0] == 0:
            pass
        else:
            self.face_right = True

        if distance >= self.speed:
            self.pos += movement.normalize() * self.speed
        else:
            if distance != 0:
                self.pos += movement.normalize() * distance
            reached = True
        self.rect.center = self.pos
        for wall in walls:
            if pygame.Rect.colliderect(wall, self.rect):
                self.rect.center = old_pos
                self.pos = old_pos
                return
            
        self.health.update(self.rect.left - 10, self.rect.top - 15)
        return reached

    def draw(self, surface, offset):
        if self.route:
            for r in self.route:
                pygame.draw.rect(surface, (0, 0, 0), r.move(offset.x, offset.y))
        surface.blit(self.image, self.rect.topleft + offset)
        self.health.draw(surface, offset)
