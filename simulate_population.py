import pygame
import numpy as np
import time
import torch



BACKGROUND_COLOR = (50,50,50) # dark grey

GAME_W = 1000
GAME_H = 1000
GAME_ROWS = 20
GAME_COLS = 20
GAME_LINESIZE = 4

SNAKE_ROWS = 12
SNAKE_COLS = 12
SNAKE_LINESIZE = 1

CHECKPOINT_GENERATIONS = 500
INPUT_SIZE = 30


from snake_cnn import snakeCNN
snakeGames = []
snakes = []
scores = []

from snake_game import snakeBoard

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
    child = snakeCNN(input_size=input_size)
    child.requires_grad_(False)
    
    geneRatio = 0.5
    # take the genes from the parents
    with torch.no_grad():
        for paramChild, paramX, paramY in zip(child.parameters(), snakeX.parameters(), snakeY.parameters()):
            if (np.random.uniform(0, 1) < geneRatio):
                paramChild.copy_(paramX)
            else:
                paramChild.copy_(paramY)
            # paramChild.copy_(geneRatio * paramX + (1 - geneRatio) * paramY)

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
    pygame.display.set_caption("Rectangle Example")
    
    clock = pygame.time.Clock()
    
    resetGames(True)
    for i in range(GAME_ROWS * GAME_COLS):
        snakes.append(snakeCNN(input_size=INPUT_SIZE))
        snakes[i].requires_grad_(False)
        scores.append(0)

    from matplotlib import pyplot as plt
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

            gHealth, gScore, gTimeAlive = snakeGames[i].extractStats()
            
            alive += (gHealth > 0)
            # a perfect snake will approach a score of 1
            # worse possible snake will approach -1
            # this formula is in range [-1, 1]
            scores[i] = (gScore - (gTimeAlive / (gScore + 1))) / (gScore + (gTimeAlive / (gScore + 1)))
            # normalize score to be in range [0, 1] and add the actual score 
            scores[i] = gScore + scores[i] * 0.5 + 0.5


            # scores[i] = (gTimeAlive + gScore * 100) / 100

        
        if (alive == 0):
            resetGames(True)

            sortedCandidates = sorted(zip(scores, snakes), key=lambda x: x[0], reverse=True)
            sortedScores, sortedSnakes = zip(*sortedCandidates)
            
            # natural selection        
            selectedCount = len(sortedSnakes) // 100 * 10
            snakes = list(sortedSnakes[0:selectedCount])
            
            sortedScores = np.array(sortedScores[:selectedCount])
            fitness = sortedScores - sortedScores.min()
            probabilities = fitness / fitness.sum()
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
            print(f"generation: {step}. score: {sortedScores[0]}")

            avgScores.append(np.mean(sortedScores))
            generations.append(step)

            plt.clf()
            plt.plot(generations, avgScores, label="Average Score")
            plt.xlabel("Generation")
            plt.ylabel("Score")
            plt.legend()
            plt.pause(0.01)  # Briefly pause to update the plot
            

            if (step % CHECKPOINT_GENERATIONS == 0):
                import os
                torch.save(snakes[0].state_dict(), os.path.join('checkpoints', f'snake-{SNAKE_ROWS}x{SNAKE_COLS}-{INPUT_SIZE}-generation-{step}.pth'))

            time.sleep(0.1)


        pygame.display.flip()
        clock.tick(1000)
