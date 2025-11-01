import pygame
import numpy as np 

EMPTY_SQUARE_COLOR = (10,10,10) # black
BODY_COLOR = (50, 205, 50)   
HEAD_COLOR = (20, 100, 20)
FRUIT_COLOR = (230, 57, 70)

EMPTY_VALUE = 0
SNAKE_VALUE = 1
FRUIT_VALUE = 2


# pygame grid has (0, 0) on top left 
# horizonal is x axis
# vertical is y axis
# snake game transforms the pygame plane into a 2d board with (1, 1) at top left 

# 0 is empty square
# 1 is snake 
# 2 is fruit
class snakeBoard:
    def __init__(self,
                 screen, 
                 posX : int, 
                 posY : int,
                 gameW : int,
                 gameH : int,
                 rows : int,
                 cols : int,
                 lineSize : int,
                 visible : bool):
        
        self.direction = np.random.randint(0, 4) # U R D L
        self.health = 50
        self.snake = []
        self.grid = []
        self.fruit = None
        self.ateFruit = False
        self.gameBoard = None
        self.timeAlive = 0


        self.screen = screen
        self.posX, self.posY = posX, posY
        self.gameW, self.gameH = gameW, gameH
        self.rows, self.cols = rows, cols
        self.lineSize = lineSize
        self.visible = visible



        self.gameBoard = [[EMPTY_VALUE for j in range(self.cols)] for i in range(self.rows)]

        dx, dy = (0, 0)
        if (self.direction == 0):
            dx = -1
        elif (self.direction == 1):
            dy = 1
        elif (self.direction == 2):
            dx = 1
        else:
            dy = -1

        # 0 <= min(x, x - dx, x -2dx). max(x, x - dx, x - 2dx) < rows
        # 0 only cares when dx is positive, rows only cares if dx is negative
        # => same logic applies to cols
        startPos = (np.random.randint(max(0, 2 * dx), min(rows, rows + 2 * dx)), np.random.randint(max(0, 2 * dy), min(cols, cols + 2 * dy)))

        
        for i in range(3):
            # later parts of snake body is just the head move in opposite direction
            self.snake.append((startPos[0] - i * dx, startPos[1] - i * dy))
            self.setgameBoard(self.snake[i], SNAKE_VALUE)
        self.fruit = self.newFruit()
        self.setgameBoard(self.fruit, FRUIT_VALUE)
        
        if not self.visible:
            return
        self.blockSizeW = (self.gameW - (self.cols + 1) * lineSize) / cols
        self.blockSizeH = (self.gameH - (self.rows + 1) * lineSize) / rows
        for i in range(self.rows):
            curRow = []
            for j in range(self.cols):
                curRow.append(pygame.Rect(self.posX + j * (self.blockSizeW + lineSize) + lineSize,
                                            self.posY + i * (self.blockSizeH + lineSize) + lineSize,
                                            self.blockSizeW, self.blockSizeH))
            self.grid.append(curRow)
        


    # checks inGrid and not snake square
    def validSquare(self, pos):
        x, y = pos
        if (x < 0) or (x >= self.rows):
            return False
        if (y < 0) or (y >= self.cols):
            return False
        
        return True
    
    def validSnake(self):
        if len(self.snake) != len(set(self.snake)):
            return False
        
        return True

    def getNewPos(self, pos, dir):
        x, y = pos
        if (dir == 0):
            return (x - 1, y)
        elif (dir == 1):
            return (x, y + 1)
        elif (dir == 2):
            return (x + 1, y)
        elif (dir == 3):
            return (x, y - 1)
    
    def newFruit(self):
        # return (self.rows // 2, self.cols // 2)
        
        available = []
        for i in range(self.rows):
            for j in range(self.cols):
                if self.gameBoard[i][j] == EMPTY_VALUE:
                    available.append((i, j))

        return available[np.random.randint(0, len(available))]

    def gameOver(self, x):
        self.health = x

    # returns health, score, time alive
    def extractStats(self):
        return (self.health, len(self.snake) - 3, self.timeAlive)

    def setgameBoard(self, pos, value):
        self.gameBoard[pos[0]][pos[1]] = value

    def drawFrame(self):
        for i in range(self.rows):
            for j in range(self.cols):
                    pygame.draw.rect(self.screen, EMPTY_SQUARE_COLOR, self.grid[i][j])

        pygame.draw.rect(self.screen, FRUIT_COLOR, self.grid[self.fruit[0]][self.fruit[1]])
        
        for i, block in enumerate(self.snake):
            x, y = block
            pygame.draw.rect(self.screen, HEAD_COLOR if (i == 0) else BODY_COLOR, self.grid[x][y])

    def snakeMove(self):
        nPos = self.getNewPos(self.snake[0], self.direction)
        if (not self.validSquare(nPos)):
            self.gameOver(-1)
            return
        
        
        # eat fruit
        if self.ateFruit:
            self.setgameBoard(self.fruit, EMPTY_VALUE)
        
        # insert new head, remove old tail
        # if just ate food then tail stays the same 
        self.snake.insert(0, nPos)
        self.setgameBoard(self.snake[0], SNAKE_VALUE)
        if not self.ateFruit:
            self.setgameBoard(self.snake[-1], SNAKE_VALUE)
            self.snake.pop()
        
        # generate new fruit
        if self.ateFruit:
            self.fruit = self.newFruit()
            self.setgameBoard(self.fruit, FRUIT_VALUE)
            self.health += 50
            self.ateFruit = False

        if (not self.validSnake()):
            self.gameOver(-1)
            return
        

        # head at fruit
        if (self.snake[0] == self.fruit):
            self.ateFruit = True

        self.health -= 1

    
    def shootRay(self, pos, dx, dy):
        distWall, distSnake, distFruit = -1, -1, -1
        
        totalDist = None
        if (abs(dx) == 1 and abs(dy) == 1):
            totalDist = min(self.rows, self.cols)
        elif (abs(dx) == 1):
            totalDist = self.rows
        else:
            totalDist = self.cols
        # we can look from both sides so + 2 to compensate, -1 because of the head
        totalDist += 1

        x, y = pos
        x += dx
        y += dy
        currentDist = 1
        
        while (self.validSquare((x, y))):
            if (self.gameBoard[x][y] == SNAKE_VALUE and distSnake == -1):
                distSnake = currentDist

            if (self.gameBoard[x][y] == FRUIT_VALUE and distFruit == -1):
                distFruit = currentDist

            currentDist += 1
            x += dx
            y += dy
        distWall = currentDist

        if (distSnake == -1):
            distSnake = totalDist
        if (distFruit == -1):
            distFruit = totalDist
        
        return (distWall / totalDist, distSnake / totalDist, distFruit / totalDist)
    
    def updateFrame(self, newDir):
        if newDir != -1:
            self.direction = newDir

        if (self.health > 0): 
            self.timeAlive += 1
            self.snakeMove()

            if self.visible:
                self.drawFrame()



    def extractStates(self):
        # look from head: 
        # in each of 8 directions, get: dist to wall, dist to body, dist to fruit
        # also 1 state for the direction of the snake 
        state = []
        
        # go through the 8 directions like a 3x3 board (except the center)
        for dx in range(-1, 2, 1):
            for dy in range(-1, 2, 1):
                if (dx == 0 and dy == 0):
                    continue
                
                dists = self.shootRay(self.snake[0], dx, dy)
                for i in range(3):
                    state.append(dists[i] * 2 - 1)
        oneHot = [0, 0, 0, 0]
        oneHot[self.direction] = 1

        for i in range(4):
            state.append(oneHot[i])

        state.append((self.fruit[0] - self.snake[0][0]) / self.rows)
        state.append((self.fruit[1] - self.snake[0][1]) / self.cols)

        return state 