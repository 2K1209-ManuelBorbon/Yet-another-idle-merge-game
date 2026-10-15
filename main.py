import pygame
from cow import Cow, collides, merge, MAX_TIER, load_sprites
from ui import Button, TextField

# --- Pygame / window setup ---
pygame.init()
WIDTH, HEIGHT = 900, 700        # Total window size
UI_BAR = 100                    # Height of the dark control bar at the top
FIELD_H = 36                    # Height of text-input boxes
FIELD_Y = 32                    # Y position of the input boxes inside the bar

# The simulation only runs in the area *below* the UI bar.
# Cow coordinates are relative to this rect, so we always add UI_BAR
# when drawing or hit-testing against real screen coordinates.
SIM_AREA = pygame.Rect(0, UI_BAR, WIDTH, HEIGHT - UI_BAR)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
load_sprites()          # ← must come after set_mode, before any Cow() is created
pygame.display.set_caption("Yet Another Idle Merge Game")
clock = pygame.time.Clock()

# --- Simulation state ---
cows = []               # List of all Cow instances currently in play
running_sim = False     # True while physics is being updated
dragged_cow = None      # The cow currently held by the mouse (or None)
drag_start_pos = None   # Where the drag began (used to detect real movement)

# --- UI widgets ---
count_field = TextField(100, FIELD_Y, 70, FIELD_H, "10")   # Number of cows to spawn
speed_field = TextField(280, FIELD_Y, 70, FIELD_H, "1.0")  # Time-scale multiplier


def start_sim():
    """Spawn a batch of cows (if none exist) and turn the simulation on."""
    global cows, running_sim
    # Only spawn a fresh batch if there are no cows yet
    if not cows:
        n = count_field.get_int(10)          # Read user input, default 10
        n = max(1, min(n, 200))              # Clamp to a sane range
        attempts = 0
        # Try to place n non-overlapping cows using rejection sampling.
        # Cap attempts at n*50 so we don't hang if the area gets too full.
        while len(cows) < n and attempts < n * 50:
            candidate = Cow(SIM_AREA.width, SIM_AREA.height)
            # Keep the candidate only if it doesn't overlap any existing cow.
            if all(not collides(candidate, c) for c in cows):
                cows.append(candidate)
            attempts += 1
    running_sim = True


def stop_sim():
    """Pause physics but keep cows on screen."""
    global running_sim
    running_sim = False


def reset_sim():
    """Clear everything and immediately spawn a fresh batch."""
    global cows, running_sim, dragged_cow
    cows = []
    dragged_cow = None
    running_sim = False
    # immediately spawn a fresh batch, or leave it for the user to press Start
    start_sim()


# --- Instantiate UI widgets (buttons are wired to the functions above) ---
start_button = Button(430, FIELD_Y, 90, FIELD_H, "Start", start_sim)
stop_button  = Button(530, FIELD_Y, 90, FIELD_H, "Stop",  stop_sim)
reset_button = Button(630, FIELD_Y, 90, FIELD_H, "Reset", reset_sim)
buttons = [start_button, stop_button, reset_button]
fields = [count_field, speed_field]


def find_cow_at(mx, my, exclude=None):
    """Return the topmost cow under the mouse, ignoring `exclude`.

    - `my` is in *screen* coordinates, so we pass `offset_y=UI_BAR`
      down to Cow.contains_point to convert into sim-space.
    - `reversed(cows)` iterates top-to-bottom so the cow drawn last
      (which is visually on top) wins the hit test.
    """
    for cow in reversed(cows):
        if cow is exclude:
            continue
        if cow.contains_point(mx, my, offset_y=UI_BAR):
            return cow
    return None


# MAIN LOOP
running = True
while running:
    # dt is seconds since last frame; multiply by user speed to get sim time.
    dt = clock.tick(60) / 1000
    speed = speed_field.get_float(1.0)
    if speed <= 0:
        speed = 1.0
    sim_dt = dt * speed
    mx, my = pygame.mouse.get_pos()

    # This must run BEFORE event processing so find_cow_at tests current positions.
    # Follow the mouse while a cow is being dragged.
    if dragged_cow is not None:
        dragged_cow.move_to(mx, my - UI_BAR)   # -UI_BAR converts screen→sim coords

    # --- THEN: process events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # --- text field focus handling ---
        # Clicking a field focuses it and unfocuses every other field.
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
            # Ignore clicks inside the UI bar (those belong to widgets).
            if event.pos[1] > UI_BAR:
                cow = find_cow_at(*event.pos)
                if cow is not None:
                    dragged_cow = cow
                    cow.dragging = True
                    drag_start_pos = event.pos
                    # Snap cow under cursor immediately on grab.
                    dragged_cow.move_to(event.pos[0], event.pos[1] - UI_BAR)

        # --- drag end / merge on release ---
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if dragged_cow is not None:
                dragged_cow.dragging = False
                # Look for a cow under the release point (excluding the one we dragged).
                target = find_cow_at(*event.pos, exclude=dragged_cow)

                # require at least 5 px of movement
                # (squared distance > 5² = 25, avoids a sqrt call)
                moved = False
                if drag_start_pos is not None:
                    dx = event.pos[0] - drag_start_pos[0]
                    dy = event.pos[1] - drag_start_pos[1]
                    moved = (dx * dx + dy * dy) > 25

                # Merge only if: the user actually dragged, there is a
                # target, both cows are the same tier, and that tier
                # isn't already maxed out.
                if (moved
                        and target is not None
                        and target is not dragged_cow
                        and target.tier == dragged_cow.tier
                        and dragged_cow.tier < MAX_TIER):
                    new_cow = merge(target, dragged_cow)
                    # Remove both parents (guard against weird duplicates).
                    if dragged_cow in cows:
                        cows.remove(dragged_cow)
                    if target in cows:
                        cows.remove(target)
                    cows.append(new_cow)

                # Clear drag state regardless of whether a merge happened.
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
        # NOTE: this section is empty — auto-merge is currently disabled.
        # The collision/merge logic above is only triggered on mouse release,
        # so cows will pass through each other while the sim is running
        # until the user manually merges them.

    # --- draw ---
    screen.fill((240, 240, 220))                                 # Field background
    pygame.draw.rect(screen, (50, 50, 60), (0, 0, WIDTH, UI_BAR))  # UI bar
    pygame.draw.line(screen, (20, 20, 20), (0, UI_BAR), (WIDTH, UI_BAR), 2)  # Separator

    font = pygame.font.SysFont("Arial", 20)
    screen.blit(font.render("Cows:", True, (230, 230, 230)), (40, 40))
    screen.blit(font.render("Speed:", True, (230, 230, 230)), (220, 40))

    count_field.draw(screen)
    speed_field.draw(screen)
    for b in buttons:
        b.draw(screen)

    # Cows are drawn in *sim* coordinates but blitted with offset_y=UI_BAR
    # so they appear below the UI bar.
    for cow in cows:
        cow.draw(screen, offset_y=UI_BAR)

    pygame.display.flip()

pygame.quit()