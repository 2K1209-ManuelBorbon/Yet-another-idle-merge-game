import pygame


# Module-level cached font. Created lazily on first use, since the font
# subsystem must be initialized first (pygame.font.init() is called by
# pygame.init() inside the main file).
FONT = None


def get_font(size=22):
    """Return a shared SysFont instance, creating it once.

    Caching the font avoids re-parsing the TTF file every frame, which
    would be a noticeable performance hit if called from draw().
    """
    global FONT
    if FONT is None:
        FONT = pygame.font.SysFont("Arial", size)
    return FONT


class Button:
    """A clickable rectangle that fires a callback when pressed."""

    def __init__(self, x, y, w, h, text, on_click):
        self.rect = pygame.Rect(x, y, w, h)   # Position & size
        self.text = text                       # Label shown on the button
        self.on_click = on_click               # Function called when clicked
        self.hovered = False                   # True while mouse is over it

    def handle_event(self, event):
        """Update hover state and fire on_click on left mouse-down."""
        if event.type == pygame.MOUSEMOTION:
            # Update hover state so draw() can lighten the color.
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Fire callback only if this click was inside the button.
            if self.rect.collidepoint(event.pos):
                self.on_click()

    def draw(self, screen):
        """Render the button: colored rounded rect + border + centered text."""
        # Slightly lighter blue when hovered, for a simple feedback effect.
        base = (70, 130, 180) if not self.hovered else (100, 160, 210)
        pygame.draw.rect(screen, base, self.rect, border_radius=6)          # Fill
        pygame.draw.rect(screen, (30, 30, 30), self.rect, width=2, border_radius=6)  # Border

        font = get_font(22)
        label = font.render(self.text, True, (255, 255, 255))  # White text
        # Center the text inside the button rectangle.
        screen.blit(label, label.get_rect(center=self.rect.center))


class TextField:
    """A single-line editable text box with basic keyboard input."""

    def __init__(self, x, y, w, h, default=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = str(default)   # Current contents as a string
        self.focused = False       # True when receiving keyboard input

    def handle_event(self, event):
        """Manage focus on click and text editing while focused."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Clicking inside focuses; clicking outside blurs.
            # (The main loop also enforces "one focused field" globally.)
            self.focused = self.rect.collidepoint(event.pos)

        elif event.type == pygame.KEYDOWN and self.focused:
            if event.key == pygame.K_BACKSPACE:
                # Delete last character.
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                # Enter defocuses — a common "commit" gesture.
                self.focused = False
            elif event.unicode.isprintable() and len(self.text) < 10:
                # Append any printable character, up to a 10-char limit.
                # isprintable() filters out control codes and weird unicode.
                self.text += event.unicode

    def get_float(self, default=0.0):
        """Parse contents as a float; return default if invalid.

        Wraps float() in try/except so the caller never has to
        deal with ValueError from empty or malformed input.
        """
        try:
            return float(self.text)
        except ValueError:
            return default

    def get_int(self, default=0):
        """Parse contents as an int; return default if invalid.

        Goes through float() first so inputs like "3.7" or "1e2"
        parse to 3 and 100 respectively instead of raising.
        """
        try:
            return int(float(self.text))
        except ValueError:
            return default

    def draw(self, screen):
        """Render the box: white fill, colored border, and text."""
        # Blue border when focused; gray otherwise.
        border = (70, 130, 180) if self.focused else (120, 120, 120)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, border_radius=4)
        pygame.draw.rect(screen, border, self.rect, width=2, border_radius=4)

        font = get_font(20)
        label = font.render(self.text, True, (20, 20, 20))
        # Small padding (8px) inside the box so text isn't flush against the border.
        screen.blit(label, (self.rect.x + 8, self.rect.y + 8))