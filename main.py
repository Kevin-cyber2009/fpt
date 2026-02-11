import pygame
import sys
from game import Game

def main():
    pygame.init()
    
    # Cấu hình màn hình
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Monster Quiz Shooter")
    
    clock = pygame.time.Clock()
    game = Game(screen)
    
    # Hide mouse cursor in game
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_event(event)
        
        game.update(dt)
        game.draw()
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()