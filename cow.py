import random
import math
import pygame

# Maximum upgrade tier an animal can reach (tiers 0..3)
MAX_TIER = 3

# File paths for the 10 animal sprites, indexed by tier.
# Tier 0 = cow, tier 1 = pig, ... tier 3 = goat. (Only the first MAX_TIER+1 are used.)
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

# Module-level list that will hold the loaded pygame Surfaces.
# Kept empty until load_sprites() is called.
SPRITES = []


def load_sprites():
    """Load and convert sprites. Call AFTER pygame.display.set_mode().

    convert_alpha() requires an initialized display to know the pixel
    format, so this must be called once the window has been created.
    """
    global SPRITES
    SPRITES = [pygame.image.load(p).convert_alpha() for p in SPRITE_PATHS]


class Cow:
    """A single animal 'blob' that bounces around the screen.

    Despite the name, the class represents any tier of animal; the
    sprite and color change based on `tier`. Higher tiers are bigger
    and get different speeds.
    """

    def __init__(self, screen_w, screen_h, tier=0, x=None, y=None, vx=None, vy=None):
        # Remember the play area bounds for wall collisions.
        self.screen_w = screen_w
        self.screen_h = screen_h

        # Tier determines size, color, and which sprite is drawn.
        self.tier = tier

        # Radius grows with tier so higher tiers feel "heavier".
        self.radius = 15 + tier * 5

        # If no position was passed in, pick a random one inside the screen.
        # (x is None means "spawn randomly"; otherwise place at given x.)
        self.x = x if x is not None else random.randint(self.radius, screen_w - self.radius)
        self.y = y if y is not None else random.randint(self.radius, screen_h - self.radius)

        # Random direction, random speed between 60 and 120 px/sec per axis.
        # random.choice([-1, 1]) flips left/right or up/down.
        self.vx = vx if vx is not None else random.choice([-1, 1]) * random.uniform(60, 120)
        self.vy = vy if vy is not None else random.choice([-1, 1]) * random.uniform(60, 120)

        # Fallback color per tier (used if we ever want to draw without a sprite).
        self.color = [(255, 255, 255), (255, 220, 150), (200, 150, 100), (150, 100, 80)][tier]

        # Flag set while the mouse is holding this animal.
        self.dragging = False

        # Pick the sprite that matches this tier.
        self.sprite = SPRITES[tier]

    def update(self, dt):
        """Advance physics by dt seconds. Skipped while being dragged."""
        if self.dragging:
            return  # position controlled by the mouse; no physics

        # Integrate position from velocity.
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Bounce off the left/right walls by clamping and reversing vx.
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx *= -1
        elif self.x + self.radius > self.screen_w:
            self.x = self.screen_w - self.radius
            self.vx *= -1

        # Same for top/bottom walls with vy.
        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy *= -1
        elif self.y + self.radius > self.screen_h:
            self.y = self.screen_h - self.radius
            self.vy *= -1

    def move_to(self, x, y):
        """Snap to a new position (used while dragging).

        Clamps to the play area so the animal can't be dragged off-screen.
        """
        self.x = max(self.radius, min(x, self.screen_w - self.radius))
        self.y = max(self.radius, min(y, self.screen_h - self.radius))

    def draw(self, screen, offset_y=0):
        """Render the sprite centered on (self.x, self.y + offset_y).

        offset_y is used for visual effects like a screen shake or to
        shift everything down (e.g., for a HUD).
        """
        # Scale the sprite so its bounding box is 2*radius wide/tall.
        size = int(self.radius * 2)
        scaled = pygame.transform.scale(self.sprite, (size, size))

        # Center the scaled sprite on the animal's position.
        rect = scaled.get_rect(center=(int(self.x), int(self.y) + offset_y))
        screen.blit(scaled, rect)

        # Draw a highlight ring while the user is dragging this animal.
        if self.dragging:
            pygame.draw.circle(screen, (255, 100, 100),
                               (int(self.x), int(self.y) + offset_y),
                               self.radius, width=3)

    def contains_point(self, px, py, offset_y=0):
        """Return True if point (px, py) is inside this animal's circle.

        Uses circle-vs-point distance test: hypot(dx, dy) <= radius.
        """
        dx = px - self.x
        dy = py - (self.y + offset_y)
        return math.hypot(dx, dy) <= self.radius


def collides(a, b):
    """Circle-vs-circle collision test.

    Two animals overlap when the distance between their centers is
    smaller than the sum of their radii.
    """
    dx = a.x - b.x
    dy = a.y - b.y
    return math.hypot(dx, dy) < a.radius + b.radius


def merge(a, b):
    """Create a new animal by combining two colliding ones.

    The new animal has tier = min(a.tier + 1, MAX_TIER), so merging
    caps out at MAX_TIER instead of crashing on out-of-range tiers.
    Its position and velocity are averages of the two parents so the
    result feels like a natural continuation of their motion.
    """
    new_tier = min(a.tier + 1, MAX_TIER)
    return Cow(
        a.screen_w, a.screen_h,
        tier=new_tier,
        x=(a.x + b.x) / 2,
        y=(a.y + b.y) / 2,
        vx=(a.vx + b.vx) / 2,
        vy=(a.vy + b.vy) / 2,
    )