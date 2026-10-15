import random
import math
import pygame

MAX_TIER = 3
# Load all 10 animal sprites once
SPRITE_PATHS = [
    "assets/cow.png",
    "assets/pig.png",
    "assets/chick.png",
    "assets/goat.png",
    "assets/horse.png",
    "assets/dog.png",
    "assets/duck.png",
    "assets/rabbit.png",
    "assets/panda.png",
    "assets/penguin.png",
]
SPRITES = []

def load_sprites():
    """Load and convert sprites. Call AFTER pygame.display.set_mode()."""
    global SPRITES
    SPRITES = [pygame.image.load(p).convert_alpha() for p in SPRITE_PATHS]

    
class Cow:
    def __init__(self, screen_w, screen_h, tier=0, x=None, y=None, vx=None, vy=None):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.tier = tier
        self.radius = 15 + tier * 5
        self.x = x if x is not None else random.randint(self.radius, screen_w - self.radius)
        self.y = y if y is not None else random.randint(self.radius, screen_h - self.radius)
        self.vx = vx if vx is not None else random.choice([-1, 1]) * random.uniform(60, 120)
        self.vy = vy if vy is not None else random.choice([-1, 1]) * random.uniform(60, 120)
        self.color = [(255, 255, 255), (255, 220, 150), (200, 150, 100), (150, 100, 80)][tier]
        self.dragging = False
        self.sprite = SPRITES[tier]

    def update(self, dt):
        if self.dragging:
            return  # position controlled by the mouse; no physics

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

    def move_to(self, x, y):
        """Snap to a new position (used while dragging)."""
        self.x = max(self.radius, min(x, self.screen_w - self.radius))
        self.y = max(self.radius, min(y, self.screen_h - self.radius))

    def draw(self, screen, offset_y=0):
        # Scale the sprite to match the cow's radius
        size = int(self.radius * 2)
        scaled = pygame.transform.scale(self.sprite, (size, size))
        
        # Center the sprite on the cow's position
        rect = scaled.get_rect(center=(int(self.x), int(self.y) + offset_y))
        screen.blit(scaled, rect)
        
        if self.dragging:
            pygame.draw.circle(screen, (255, 100, 100), 
                            (int(self.x), int(self.y) + offset_y), 
                            self.radius, width=3)

    def contains_point(self, px, py, offset_y=0):
        dx = px - self.x
        dy = py - (self.y + offset_y)
        return math.hypot(dx, dy) <= self.radius


def collides(a, b):
    dx = a.x - b.x
    dy = a.y - b.y
    return math.hypot(dx, dy) < a.radius + b.radius


def merge(a, b):
    new_tier = min(a.tier + 1, MAX_TIER)
    return Cow(
        a.screen_w, a.screen_h,
        tier=new_tier,
        x=(a.x + b.x) / 2,
        y=(a.y + b.y) / 2,
        vx=(a.vx + b.vx) / 2,
        vy=(a.vy + b.vy) / 2,
    )