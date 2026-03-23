# Kalaha AI

A Python implementation of the classic board game Kalaha, featuring a playable terminal interface with an AI opponent, and a match setup with AI vs. AI experiments. 

## Overview

This project provides a complete engine for playing Kalaha, along with an AI that can use **Minimax** or **Minimax with Alpha-Beta pruning** to decide on the best possible moves. You can play directly against the AI in your terminal or make AI's play against each other.

## Features

- **Playable in the terminal** through `main_play.py`
- **Kalaha game engine** with legal move generation, captures, extra turns, terminal detection, and score collection
- **Search-based AI** using either:
  - Minimax
  - Minimax with Alpha-Beta pruning
- **Experiment runner** for AI vs AI matches with timing and search statistics
- **Custom evaluation functions** for testing different heuristics

## Project Structure

- **`main_play.py`**: The main entry point to play against an AI in the terminal. It handles the game loop, takes input from the human player, and prints the current state of the board to the terminal.
- **`main_AIs_play.py`**: Runs AI-vs-AI matches and multi-game experiments printing performance metrics after. This is for benchmarking methods against each other.
- **`game_engine.py`**: The core game logic. It manages the `GameState`, determines legal moves, distributes stones across pits according to the rules of Kalaha, and evaluates game-over conditions.
- **`ai_player.py`**: Contains the artificial intelligence implementation. The AI uses the Minimax algorithm enhanced with Alpha-Beta pruning to evaluate future board states (up to a default depth of 6) and select the optimal move.
- **`ai_mult_player.py`**: AI player with adadded metrics such as expanded nodes, cutoffs and chosen moves.
- **`ai_mult_player_mult_eval.py`**: Extended AI player that supports custom evaluation functions.


## Requirements

- Python 3.8 or higher. 
- No external dependencies are required (relies only on Python's standard library).

## How to Play Against the AI

Run the main file with Python:

```bash
python3 main_play.py
```

### Gameplay Rules
- **Player 1 (You)** play on the bottom row and your goal is to collect stones in the rightmost store.
- **Player 2 (AI)** plays on the top row and collects stones in the leftmost store.
- During your turn, select one of your pits (numbered 1-6 from left to right) by entering its number. The stones in that pit will be shown counter-clockwise.

## How the AI works
The AI explores future board states using Minimax search.
- Set `stones_per_pit=6` for the standard kalaha game, but this can be changed to all positive int over zero. 
- Set `flag=True` to use additional **Alpha-Beta pruning**
- Set `flag=False` to use plain **Minimax**
- Set `max_depth` to control how many depths in the search tree are explored.

Example from `main_play.py`:

```python
game = KalahaGame(stones_per_pit=6, max_depth=6, flag=True)
```

## Running AI vs AI Experiments
Run:
```bash
python3 main_AIs_play.py
```

This mode supports:
- different search depths for each AI,
- Alpha-Beta on/off for each side,
- custom evaluation functions,
- aggregate experiment statistics across many games.
- time limit per move (Tlim)
- number of games in the experiment

Note that the starting player is chosen randomly in `game_engine.py` as to not have bias.

### Reported Metrics

The experiment runner can report:

- winner and final scores,
- score difference,
- total moves,
- average move time,
- nodes expanded,
- Alpha-Beta cutoffs,
- search depth and pruning configuration.

## Evaluation Functions

`main_AIs_play.py` includes several example heuristics:
- `eval_store_heavy` — favors stones already secured in the store
- `eval_side_heavy` — balances store advantage and side control
- `eval_extra_turns` — rewards positions that create extra-turn opportunities
- `eval_13pit` - rewards positions with pits having 13 marbles, as this activate the capture rule.

One could define new evaluation function with the same signature:

```python
def my_eval(state, ai):
    return X
```

and pass it into the AI constructor used by the experiment runner.
