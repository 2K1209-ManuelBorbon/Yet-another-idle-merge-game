import pygame


FONT = None


def get_font(size=22):
    global FONT
    if FONT is None:
        FONT = pygame.font.SysFont("Arial", size)
    return FONT


class Button:
    def __init__(self, x, y, w, h, text, on_click):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.on_click = on_click
        self.hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.on_click()

    def draw(self, screen):
        base = (70, 130, 180) if not self.hovered else (100, 160, 210)
        pygame.draw.rect(screen, base, self.rect, border_radius=6)
        pygame.draw.rect(screen, (30, 30, 30), self.rect, width=2, border_radius=6)
        font = get_font(22)
        label = font.render(self.text, True, (255, 255, 255))
        screen.blit(label, label.get_rect(center=self.rect.center))


class TextField:
    def __init__(self, x, y, w, h, default=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = str(default)
        self.focused = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.focused = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.focused:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.focused = False
            elif event.unicode.isprintable() and len(self.text) < 10:
                self.text += event.unicode

    def get_float(self, default=0.0):
        try:
            return float(self.text)
        except ValueError:
            return default

    def get_int(self, default=0):
        try:
            return int(float(self.text))
        except ValueError:
            return default

    def draw(self, screen):
        border = (70, 130, 180) if self.focused else (120, 120, 120)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, border_radius=4)
        pygame.draw.rect(screen, border, self.rect, width=2, border_radius=4)
        font = get_font(20)
        label = font.render(self.text, True, (20, 20, 20))
        screen.blit(label, (self.rect.x + 8, self.rect.y + 8))