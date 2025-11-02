import pygame
import numpy as np
import time
import torch
import os 

from snake_mlp import snakeMLP
from snake_game import snakeBoard
from matplotlib import pyplot as plt


SEED = 7
np.random.seed(SEED)
torch.manual_seed(SEED)

BACKGROUND_COLOR = (50,50,50) # dark grey

GAME_W = 1000
GAME_H = 1000
GAME_ROWS = 20
GAME_COLS = 20
GAME_LINESIZE = 2

SNAKE_ROWS = 10
SNAKE_COLS = 10
SNAKE_LINESIZE = 1

CHECKPOINT_GENERATIONS = 125
INPUT_SIZE = 32


snakeGames = []
snakes = []
scores = []


def resetGames(isVisible):
    snakeGames.clear()

    snakeW = (GAME_W - (GAME_COLS - 1) * GAME_LINESIZE) / GAME_COLS 
    snakeH = (GAME_H - (GAME_ROWS - 1) * GAME_LINESIZE) / GAME_ROWS
    for i in range(GAME_ROWS):
        for j in range(GAME_COLS):
            snakeGames.append(snakeBoard(screen, j * (snakeW + GAME_LINESIZE), i * (snakeH + GAME_LINESIZE),
                                          snakeW, snakeH, 
                                          SNAKE_ROWS, SNAKE_COLS, 
                                          SNAKE_LINESIZE, visible=isVisible))

def breedSnake(snakeX, snakeY, input_size):
    child = snakeMLP(input_size=input_size)
    child.requires_grad_(False)
    
    geneRatio = 0.5
    # take the genes from the parents
    with torch.no_grad():
        for paramChild, paramX, paramY in zip(child.parameters(), snakeX.parameters(), snakeY.parameters()):
            # if (np.random.uniform(0, 1) < geneRatio):
            #     paramChild.copy_(paramX)
            # else:
            #     paramChild.copy_(paramY)
            paramChild.copy_(geneRatio * paramX + (1 - geneRatio) * paramY)

    # mutate the child
    mutationRate = 0.5
    mutationEpsilon = 0.3
    with torch.no_grad():
        for paramChild in child.parameters():
            if (np.random.uniform(0, 1) < mutationRate):
                paramChild.add_(torch.randn_like(paramChild) * mutationEpsilon)
            paramChild.clamp_(-5, 5)
    
    return child


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((GAME_W, GAME_H))
    pygame.display.set_caption("Genetic Snake Game")
    
    clock = pygame.time.Clock()
    
    GAMES_VISIBLE = True
    resetGames(GAMES_VISIBLE)
    for i in range(GAME_ROWS * GAME_COLS):
        snakes.append(snakeMLP(input_size=INPUT_SIZE))
        snakes[i].requires_grad_(False)
        scores.append(0)

    plt.ion()  # interactive mode
    plt.figure()

    avgScores = []
    generations = []

    step = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    

        rect = pygame.Rect(0, 0, GAME_W, GAME_H)
        pygame.draw.rect(screen, BACKGROUND_COLOR, rect)

        

        alive =  0
        for i in range(len(snakeGames)):
            newDir = snakes[i](snakeGames[i].extractStates())
            snakeGames[i].updateFrame(newDir)

            gHealth, gScore, gTimeAlive, gLastAte, gSeen = snakeGames[i].extractStats()
            alive += (gHealth > 0)

            scores[i] = gScore - gTimeAlive / 100

        
        if (alive == 0):
            resetGames(GAMES_VISIBLE)

            sortedCandidates = sorted(zip(scores, snakes), key=lambda x: x[0], reverse=True)
            sortedScores, sortedSnakes = zip(*sortedCandidates)
            
            # natural selection        
            selectedCount = len(sortedSnakes) // 100 * 10
            snakes = list(sortedSnakes[0:selectedCount])
            
            sortedScores = np.array(sortedScores[:selectedCount])
            fitness = sortedScores - sortedScores.min()
            probabilities = fitness / fitness.sum()
            # print(fitness)
            print(probabilities[:10])
            
            # taking the genes from the selected snakes
            # choose 2 parents
            # take their genes and mutate
            while (len(snakes) < GAME_ROWS * GAME_COLS):
                # tournament selection
                randomParents = np.random.choice(selectedCount, size=2, p=probabilities)
                
                snakes.append(breedSnake(sortedSnakes[randomParents[0]], sortedSnakes[randomParents[1]], INPUT_SIZE))

            scores = [0] * len(snakes)


            

            # loggin metrics
            step += 1   
            print(f"generation: {step}. max score: {sortedScores[0]}. avg score: {np.mean(sortedScores)}")

            avgScores.append(np.mean(sortedScores))
            generations.append(step)

            plt.clf()
            plt.plot(generations, avgScores, label="Average Score")
            plt.xlabel("Generation")
            plt.ylabel("Score")
            plt.legend()
            plt.pause(0.01)  # Briefly pause to update the plot
            

            if (step % CHECKPOINT_GENERATIONS == 0):
                ckpt_path = f'snake-inp{INPUT_SIZE}-{SNAKE_ROWS}x{SNAKE_COLS}-pop{GAME_ROWS * GAME_COLS}-gen{step}-seed{SEED}.pth'
                checkpoint = {
                    'generation': step,
                    'population': [snake.state_dict() for snake in sortedSnakes],
                    'scores': list(sortedScores),
                    'config': {
                        'SEED': SEED,
                        'SNAKE_ROWS': SNAKE_ROWS,
                        'SNAKE_COLS': SNAKE_COLS,
                        'INPUT_SIZE': INPUT_SIZE,
                        'GAME_ROWS': GAME_ROWS,
                        'GAME_COLS': GAME_COLS
                    },
                    'metrics': {
                        'generations': list(generations),
                        'avgScores': list(avgScores)
                    } 
                }
                torch.save(checkpoint, os.path.join('checkpoints', ckpt_path))
                plt.savefig(f"checkpoints/plot-gen-{step}.jpg")

            time.sleep(0.1)


        pygame.display.flip()
        clock.tick(1000)
