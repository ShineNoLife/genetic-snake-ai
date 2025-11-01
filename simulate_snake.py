import pygame
import numpy as np
import time
import torch



BACKGROUND_COLOR = (50,50,50) # dark grey

GAME_W = 1000
GAME_H = 1000

SNAKE_ROWS = 6
SNAKE_COLS = 6
SNAKE_LINESIZE = 1

CHECKPOINT_GENERATIONS = 500
INPUT_SIZE = 30


from snake_cnn import snakeCNN
from snake_game import snakeBoard
snakeGame = None
snake = None


def newGame():
    return snakeBoard(screen, 0, 0,
                                    GAME_W, GAME_H, 
                                    SNAKE_ROWS, SNAKE_COLS, 
                                    SNAKE_LINESIZE, visible=True)


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((GAME_W, GAME_H))
    pygame.display.set_caption("Rectangle Example")
    
    clock = pygame.time.Clock()
    
    snakeGame = newGame()
    snake = snakeCNN(input_size=INPUT_SIZE)
    
    import os
    ckptDir = os.path.join("checkpoints", "snake-12x12-30-generation-1500.pth")
    state_dicst = torch.load(ckptDir, weights_only=True)
    snake.load_state_dict(state_dicst)

    step = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    

        rect = pygame.Rect(0, 0, GAME_W, GAME_H)
        pygame.draw.rect(screen, BACKGROUND_COLOR, rect)

        
        newDir = snake(snakeGame.extractStates())
        snakeGame.updateFrame(newDir)

        if (snakeGame.health <= 0):
            snakeGame = newGame()
            time.sleep(1)


        pygame.display.flip()
        clock.tick(5)
