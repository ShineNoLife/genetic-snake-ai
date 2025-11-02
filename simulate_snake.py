import pygame
import numpy as np
import time
import torch
import os 

from snake_mlp import snakeMLP
from snake_game import snakeBoard


BACKGROUND_COLOR = (50,50,50) # dark grey

GAME_W = 1000
GAME_H = 1000

SNAKE_ROWS = 10
SNAKE_COLS = 10
SNAKE_LINESIZE = 1

INPUT_SIZE = 32


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
    pygame.display.set_caption("Genetic Snake Game")
    
    clock = pygame.time.Clock()
    
    snakeGame = newGame()
    snake = snakeMLP(input_size=INPUT_SIZE)
    
    ckptDir = os.path.join("checkpoints", "v1", "snake-inp32-10x10-pop400-gen1000-seed7.pth")
    state_dicst = torch.load(ckptDir)
    snake.load_state_dict(state_dicst['population'][0])
    
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

        gHealth, gScore, gTimeAlive, gLastAte, gSeen = snakeGame.extractStats()
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {gScore}", True, (255, 255, 255))
        health_text = font.render(f"Health: {gHealth}", True, (255, 255, 255))

        screen.blit(score_text, (10, 10))      # Top-left corner
        screen.blit(health_text, (10, 50)) 

        if (snakeGame.health <= 0):
            snakeGame = newGame()
            time.sleep(1)


        pygame.display.flip()
        clock.tick(30)
