import pygame
from cow import Cow, collides, merge, MAX_TIER, load_sprites
from ui import Button, TextField

pygame.init()
WIDTH, HEIGHT = 900, 700
UI_BAR = 100
FIELD_H = 36
FIELD_Y = 32
SIM_AREA = pygame.Rect(0, UI_BAR, WIDTH, HEIGHT - UI_BAR)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
load_sprites()          # ← must come after set_mode, before any Cow() is created
pygame.display.set_caption("Yet Another Idle Merge Game")
clock = pygame.time.Clock()

cows = []
running_sim = False
dragged_cow = None
drag_start_pos = None

# --- UI ---
count_field = TextField(100, FIELD_Y, 70, FIELD_H, "10")
speed_field = TextField(280, FIELD_Y, 70, FIELD_H, "1.0")

def start_sim():
    global cows, running_sim
    # Only spawn a fresh batch if there are no cows yet
    if not cows:
        n = count_field.get_int(10)
        n = max(1, min(n, 200))
        attempts = 0
        while len(cows) < n and attempts < n * 50:
            candidate = Cow(SIM_AREA.width, SIM_AREA.height)
            if all(not collides(candidate, c) for c in cows):
                cows.append(candidate)
            attempts += 1
    running_sim = True

def stop_sim():
    global running_sim
    running_sim = False

def reset_sim():
    global cows, running_sim, dragged_cow
    cows = []
    dragged_cow = None
    running_sim = False
    # immediately spawn a fresh batch, or leave it for the user to press Start
    start_sim()

start_button = Button(430, FIELD_Y, 90, FIELD_H, "Start", start_sim)
stop_button  = Button(530, FIELD_Y, 90, FIELD_H, "Stop",  stop_sim)
reset_button = Button(630, FIELD_Y, 90, FIELD_H, "Reset", reset_sim)
buttons = [start_button, stop_button, reset_button]
fields = [count_field, speed_field]


def find_cow_at(mx, my, exclude=None):
    """Return the topmost cow under the mouse, ignoring `exclude`."""
    for cow in reversed(cows):
        if cow is exclude:
            continue
        if cow.contains_point(mx, my, offset_y=UI_BAR):
            return cow
    return None


running = True
while running:
    dt = clock.tick(60) / 1000
    speed = speed_field.get_float(1.0)
    if speed <= 0:
        speed = 1.0
    sim_dt = dt * speed
    mx, my = pygame.mouse.get_pos()

    # This must run BEFORE event processing so find_cow_at tests current positions.
    if dragged_cow is not None:
        dragged_cow.move_to(mx, my - UI_BAR)

    # --- THEN: process events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # --- text field focus handling ---
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked_field = None
            for f in fields:
                if f.rect.collidepoint(event.pos):
                    clicked_field = f
                    break
            for f in fields:
                f.focused = (f is clicked_field)

        # --- drag start ---
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if event.pos[1] > UI_BAR:
                cow = find_cow_at(*event.pos)
                if cow is not None:
                    dragged_cow = cow
                    cow.dragging = True
                    drag_start_pos = event.pos
                    dragged_cow.move_to(event.pos[0], event.pos[1] - UI_BAR)

        # --- drag end / merge on release ---
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if dragged_cow is not None:
                dragged_cow.dragging = False
                target = find_cow_at(*event.pos, exclude=dragged_cow)

                # require at least 5 px of movement
                moved = False
                if drag_start_pos is not None:
                    dx = event.pos[0] - drag_start_pos[0]
                    dy = event.pos[1] - drag_start_pos[1]
                    moved = (dx * dx + dy * dy) > 25

                if (moved
                        and target is not None
                        and target is not dragged_cow
                        and target.tier == dragged_cow.tier
                        and dragged_cow.tier < MAX_TIER):
                    new_cow = merge(target, dragged_cow)
                    if dragged_cow in cows:
                        cows.remove(dragged_cow)
                    if target in cows:
                        cows.remove(target)
                    cows.append(new_cow)

                dragged_cow = None
                drag_start_pos = None

        # --- pass event to UI widgets ---
        for f in fields:
            f.handle_event(event)
        for b in buttons:
            b.handle_event(event)

    # --- simulation update ---
    if running_sim:
        for cow in cows:
            cow.update(sim_dt)

        # auto-merge on collision


    # --- draw ---
    screen.fill((240, 240, 220))
    pygame.draw.rect(screen, (50, 50, 60), (0, 0, WIDTH, UI_BAR))
    pygame.draw.line(screen, (20, 20, 20), (0, UI_BAR), (WIDTH, UI_BAR), 2)

    font = pygame.font.SysFont("Arial", 20)
    screen.blit(font.render("Cows:", True, (230, 230, 230)), (40, 40))
    screen.blit(font.render("Speed:", True, (230, 230, 230)), (220, 40))

    count_field.draw(screen)
    speed_field.draw(screen)
    for b in buttons:
        b.draw(screen)

    for cow in cows:
        cow.draw(screen, offset_y=UI_BAR)

    pygame.display.flip()

pygame.quit()