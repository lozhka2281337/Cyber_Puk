import generate
import pygame

pygame.init()

screen = pygame.display.set_mode((1280, 960))
pygame.display.set_caption("BSP Map Generation")

surface = generate.get_map()

running = True
while (running):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # выход на esc
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                surface = generate.get_map()

    screen.fill("green")
    screen.blit(surface, (0, 0))
    pygame.display.flip()


pygame.quit()