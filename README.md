# Genetic Snake AI

Simulating a population of MLPs to learn the snake game using a Genetic Algorithm.


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
├── snake_cnn.py           # mlp architecture 
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