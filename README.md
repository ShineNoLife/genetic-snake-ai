# Genetic Snake AI

Simulating a population of MLPs to learn the snake game using a Genetic Algorithm.

In the genetic algorithm, there's:
- `Simulation phase`: the snakes play their own game until they die
- `Fitness scoring phase`: each snakes are given a fitness score on how well they played the game 
- `Elitism phase`: select the snakes with the best scores as gene seeds for the next generation
- `Crossover phase`: the genes from the elites are used to create new snakes for the next generation
- `Mutation phase`: the newly created snakes have a chance to mutate

After these phases, we're ready to start simulating a new generation. This continues generations after generations, the snakes with the best strategy will prevail and reproduce, leading to the population gradually changing for the better.

# Installation

```bash
git clone https://github.com/yourusername/genetic-snake-ai.git
cd genetic-snake-ai
pip install torch pygame matplotlib numpy
```

# Usage

Simulating a population from scratch
```bash
python simulate_population.py
```

Simulate a snake from a checkpoint
```bash
python simulate_snake.py
```

# Key Parameters
```python
GAME_ROWS = 20          # Population grid rows
GAME_COLS = 20          # Population grid columns  
SNAKE_ROWS = 10         # Game grid size
SNAKE_COLS = 10
INPUT_SIZE = 32         # Neural network input size
CHECKPOINT_GENERATIONS = 250  # Save frequency
```

## File Structure

```
genetic-snake-ai/
├── snake_game.py          # Core Snake game logic
├── snake_mlp.py           # mlp architecture 
├── simulate_population.py # Population training script
├── simulate_snake.py      # Single agent testing
├── checkpoints/           # Saved model generations
└── README.md
```

# SnakeV1

see more detailed configs in [v1/README.md](v1/README.md)

![](v1/snakev1.jpg)

Generation 125:

![](v1/gen125.gif)

Generation 250:

![](v1/gen250.gif)

Generation 1000:

![](v1/gen1000.gif)