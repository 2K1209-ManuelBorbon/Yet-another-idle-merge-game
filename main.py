import pygame
from cow import Cow, collides, merge

pygame.init()
WIDTH, HEIGHT = 900, 700
MAX_TIER = 3
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Yet Another Idle Merge Game")
clock = pygame.time.Clock()

cows = [Cow(WIDTH, HEIGHT) for _ in range(10)]

running = True
while running:
    dt = clock.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for cow in cows:
        cow.update(dt)

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
    screen.fill((240, 240, 220))
    for cow in cows:
        cow.draw(screen)
    pygame.display.flip()

pygame.quit()