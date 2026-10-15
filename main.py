import pygame
from cow import Cow, collides, merge, MAX_TIER
from ui import Button, TextField

pygame.init()
WIDTH, HEIGHT = 900, 700
SIM_AREA = pygame.Rect(0, 100, WIDTH, HEIGHT - 100)  # play area below the UI bar
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Yet Another Idle Merge Game")
clock = pygame.time.Clock()

# --- state ---
cows = []
running_sim = False

# --- UI ---
count_field = TextField(120, 30, 80, 36, "10")
speed_field = TextField(330, 30, 80, 36, "1.0")

def start_sim():
    global cows, running_sim
    n = count_field.get_int(10)
    n = max(1, min(n, 200))  # clamp to sane range
    cows = [Cow(SIM_AREA.width, SIM_AREA.height) for _ in range(n)]
    running_sim = True

def stop_sim():
    global running_sim
    running_sim = False

start_button = Button(20, 30, 80, 36, "Start", start_sim)
stop_button  = Button(440, 30, 80, 36, "Stop", stop_sim)

buttons = [start_button, stop_button]
fields = [count_field, speed_field]

# --- main loop ---
running = True
while running:
    dt = clock.tick(60) / 1000
    speed = speed_field.get_float(1.0)
    if speed <= 0:
        speed = 1.0
    sim_dt = dt * speed

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Only let one field be focused at a time
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked_field = None
            for f in fields:
                if f.rect.collidepoint(event.pos):
                    clicked_field = f
                    break
            for f in fields:
                f.focused = (f is clicked_field)

        for f in fields:
            f.handle_event(event)
        for b in buttons:
            b.handle_event(event)

    # --- update simulation ---
    if running_sim:
        for cow in cows:
            cow.update(sim_dt)

        new_cows = []
        merged = set()
        for i, a in enumerate(cows):
            if i in merged:
                continue
            for j, b in enumerate(cows):
                if j <= i or j in merged:
                    continue
                if a.tier == b.tier and a.tier < MAX_TIER and collides(a, b):
                    new_cows.append(merge(a, b))
                    merged.add(i)
                    merged.add(j)
                    break
            else:
                if i not in merged:
                    new_cows.append(a)
        cows = new_cows

    # --- draw ---
    screen.fill((240, 240, 220))

    # UI bar background
    pygame.draw.rect(screen, (50, 50, 60), (0, 0, WIDTH, 100))
    pygame.draw.line(screen, (20, 20, 20), (0, 100), (WIDTH, 100), 2)

    font = pygame.font.SysFont("Arial", 20)
    screen.blit(font.render("Cows:", True, (230, 230, 230)), (60, 38))
    screen.blit(font.render("Speed:", True, (230, 230, 230)), (260, 38))

    count_field.draw(screen)
    speed_field.draw(screen)
    for b in buttons:
        b.draw(screen)

    # draw cows offset into the sim area (below the UI bar)
    for cow in cows:
        cow.draw(screen, offset_y=100)

    pygame.display.flip()

pygame.quit()