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
        self.dx, self.dy = [-1, 0, 1, 0], [0, 1, 0, -1]
        self.health = 50
        self.snake = []
        self.grid = []
        self.seen = []
        self.fruit = None
        self.ateFruit = False
        self.gameBoard = None
        self.timeAlive, self.lastAte = 0, 0


        self.screen = screen
        self.posX, self.posY = posX, posY
        self.gameW, self.gameH = gameW, gameH
        self.rows, self.cols = rows, cols
        self.lineSize = lineSize
        self.visible = visible



        self.gameBoard = [[EMPTY_VALUE for j in range(self.cols)] for i in range(self.rows)]
        self.seen = [[False for j in range(self.cols)] for i in range(self.rows)]

        cdx, cdy = self.dx[self.direction], self.dy[self.direction]

        # 0 <= min(x, x - dx, x -2dx). max(x, x - dx, x - 2dx) < rows
        # 0 only cares when dx is positive, rows only cares if dx is negative
        # => same logic applies to cols
        startPos = (np.random.randint(max(0, 2 * cdx), min(rows, rows + 2 * cdx)), np.random.randint(max(0, 2 * cdy), min(cols, cols + 2 * cdy)))

        
        for i in range(3):
            # later parts of snake body is just the head move in opposite direction
            self.snake.append((startPos[0] - i * cdx, startPos[1] - i * cdy))
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
        totalSeen = 0
        for i in range(self.rows):
            for j in range(self.cols):
                totalSeen += self.seen[i][j]

        return (self.health, len(self.snake) - 3, self.timeAlive, self.lastAte, totalSeen)

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

    # snake will extends at the exact turn it eat fruit, not the turn after
    def snakeMove(self):
        nPos = self.getNewPos(self.snake[0], self.direction)
        if (not self.validSquare(nPos)):
            self.gameOver(-1)
            return
        
        self.ateFruit = (nPos == self.fruit)

        # insert new head, remove old tail
        # if just ate food then tail stays the same 
        self.snake.insert(0, nPos)
        self.setgameBoard(self.snake[0], SNAKE_VALUE)
        if not self.ateFruit:
            self.setgameBoard(self.snake[-1], EMPTY_VALUE)
            self.snake.pop()
        self.seen[self.snake[0][0]][self.snake[0][1]] = True

        if (not self.validSnake()):
            self.gameOver(-1)
            return
        

        # generate new fruit
        if self.ateFruit:
            self.fruit = self.newFruit()
            self.setgameBoard(self.fruit, FRUIT_VALUE)

            self.health += 50
            self.lastAte = self.timeAlive

        self.health -= 1

    
    def shootRay(self, pos, cdx, cdy):
        distWall, distSnake, distFruit = -1, -1, -1

        x, y = pos
        x += cdx
        y += cdy
        currentDist = 1
        
        while (self.validSquare((x, y))):
            if (self.gameBoard[x][y] == SNAKE_VALUE and distSnake == -1):
                distSnake = currentDist

            if (self.gameBoard[x][y] == FRUIT_VALUE and distFruit == -1):
                distFruit = 1

            currentDist += 1
            x += cdx
            y += cdy
        distWall = currentDist
        
        if (distFruit == -1):
            distFruit = 0
        
        return (distWall == 1, distSnake == 1, distFruit)
    
    def updateFrame(self, newDir):
        if (newDir == 0): # turn left
            self.direction = (self.direction + 3) % 4
        elif (newDir == 2): # turn right
            self.direction = (self.direction + 1) % 4

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
                    state.append(dists[i])
        tmp = [0, 0, 0, 0]
        tmp[self.direction] = 1

        for i in range(4):
            state.append(tmp[i])

        tmp = [0, 0, 0, 0]
        if (self.fruit[0] >= self.snake[0][0]):
            tmp[0] = 1
        else:
            tmp[1] = 1
        if (self.fruit[1] >= self.snake[0][1]):
            tmp[2] = 1
        else:
            tmp[3] = 1

        for i in range(4):
            state.append(tmp[i])

        # print(state)
        return state 
    
    def evaluateMove(self, newDir):
        points = 0

        points -= 1.5
        nPos = (self.snake[0][0] + self.dx[newDir], self.snake[0][1] + self.dy[newDir])
        if (nPos == self.fruit):
            points += 1000
        
        if (abs(self.fruit[0] - nPos[0]) < abs(self.fruit[0] - self.snake[0][0]) \
            or abs(self.fruit[1] - nPos[1]) < abs(self.fruit[1] - self.snake[0][1])):
            points += 1

        return points