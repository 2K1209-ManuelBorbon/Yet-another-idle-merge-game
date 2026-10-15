import random
import math
import pygame

MAX_TIER = 3

class Cow:
    def __init__(self, screen_w, screen_h, tier = 0, x = None, y = None, vx = None, vy = None):
        self.screen_w = screen_w
        self.screen_h = screen_h        
        self.tier = tier
        self.radius = 15 + tier * 5
        self.x = x if x is not None else random.randint(self.radius, screen_w - self.radius)
        self.y = y if y is not None else random.randint(self.radius, screen_h - self.radius)
        self.vx = vx if vx is not None else random.choice([-1, 1]) * random.uniform(60, 120)
        self.vy = vy if vy is not None else random.choice([-1, 1]) * random.uniform(60, 120)
        self.color = [(255,255,255), (255,220,150), (200,150,100), (150,100,80)][tier]

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
    
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx *= -1
        elif self.x + self.radius > self.screen_w:
            self.x = self.screen_w - self.radius
            self.vx *= -1
    
        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy *= -1
        elif self.y + self.radius > self.screen_h:
            self.y = self.screen_h - self.radius
            self.vy *= -1

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

def collides(a, b):
    dx = a.x - b.x
    dy = a.y - b.y
    return math.hypot(dx, dy) < a.radius + b.radius

def merge(a, b):
    """Combine two same-tier cows into one higher-tier cow."""
    new_tier = min(a.tier + 1, MAX_TIER)
    return Cow(
        a.screen_w, a.screen_h,
        tier=new_tier,
        x=(a.x + b.x) / 2,
        y=(a.y + b.y) / 2,
        vx=(a.vx + b.vx) / 2,
        vy=(a.vy + b.vy) / 2,
    )